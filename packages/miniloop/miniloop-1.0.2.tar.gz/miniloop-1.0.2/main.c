// SPDX-License-Identifier: Apache-2.0
// Author: Qiyaya
#include <Python.h>
#include <stdbool.h>
#include <time.h>

#ifdef _WIN32
#include <windows.h>
#define sleep_ms(ms) Sleep(ms)
#else
#include <unistd.h>
#endif

static PyObject *update_callback = NULL;
static PyObject *render_callback = NULL;
static double target_fps = 60.0;
static bool running = false;

#ifdef _WIN32
static void enable_high_precision_timer() {
    timeBeginPeriod(1);
}
#endif

static double get_time() {
#ifdef _WIN32
    LARGE_INTEGER frequency, counter;
    QueryPerformanceFrequency(&frequency);
    QueryPerformanceCounter(&counter);
    return (double)counter.QuadPart / (double)frequency.QuadPart;
#else
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + ts.tv_nsec / 1.0e9;
#endif
}

static void precise_sleep(double seconds) {
#ifdef _WIN32
    Sleep((DWORD)(seconds * 1000));
#else
    struct timespec ts;
    ts.tv_sec = (time_t)seconds;
    ts.tv_nsec = (long)((seconds - ts.tv_sec) * 1e9);
    nanosleep(&ts, NULL);
#endif
}

// Process function for update loop
static void update_process(PyObject *update_func, double delta_time) {
    if (update_func && PyCallable_Check(update_func)) {
        PyObject *arg = PyFloat_FromDouble(delta_time);
        PyObject *result = PyObject_CallObject(update_func, PyTuple_Pack(1, arg));
        Py_DECREF(arg);
        if (!result) {
            PyErr_Print();
        }
        Py_XDECREF(result);
    }
}

// Process function for render loop
static void render_process(PyObject *render_func) {
    if (render_func && PyCallable_Check(render_func)) {
        PyObject *result = PyObject_CallObject(render_func, NULL);
        if (!result) {
            PyErr_Print();
        }
        Py_XDECREF(result);
    }
}

static PyObject* start_game_loop(PyObject *self, PyObject *args) {
    if (!update_callback || !render_callback) {
        PyErr_SetString(PyExc_RuntimeError, "Update and render callbacks must be set first.");
        return NULL;
    }

#ifdef _WIN32
    enable_high_precision_timer();
#endif

    running = true;
    double frame_time = 1.0 / target_fps;
    double previous_time = get_time();
    double delta_time;

    Py_BEGIN_ALLOW_THREADS

    while (running) {
        double current_time = get_time();
        delta_time = current_time - previous_time;
        previous_time = current_time;

        // Spawn update and render processes
        PyThreadState *tstate = PyGILState_GetThisThreadState();
        if (tstate != NULL) PyEval_SaveThread();

        PyGILState_STATE gstate = PyGILState_Ensure();
        PyObject *update_proc = Py_BuildValue("(O,d)", update_callback, delta_time);
        PyObject *render_proc = Py_BuildValue("(O)", render_callback);

        if (update_proc && render_proc) {
            PyObject *multiprocessing = PyImport_ImportModule("multiprocessing");
            if (multiprocessing) {
                PyObject *Process = PyObject_GetAttrString(multiprocessing, "Process");

                if (Process) {
                    PyObject *update_args = PyTuple_Pack(2, Py_None, update_proc);
                    PyObject *render_args = PyTuple_Pack(2, Py_None, render_proc);

                    PyObject *update_p = PyObject_Call(Process, update_args, NULL);
                    PyObject *render_p = PyObject_Call(Process, render_args, NULL);

                    if (update_p && render_p) {
                        PyObject_CallMethod(update_p, "start", NULL);
                        PyObject_CallMethod(render_p, "start", NULL);

                        PyObject_CallMethod(update_p, "join", NULL);
                        PyObject_CallMethod(render_p, "join", NULL);

                        Py_XDECREF(update_p);
                        Py_XDECREF(render_p);
                    }

                    Py_XDECREF(update_args);
                    Py_XDECREF(render_args);
                    Py_XDECREF(Process);
                }
                Py_XDECREF(multiprocessing);
            }
        }

        Py_XDECREF(update_proc);
        Py_XDECREF(render_proc);

        PyGILState_Release(gstate);

        // Maintain FPS timing
        double sleep_time = frame_time - (get_time() - previous_time);
        if (sleep_time > 0 && running) {
            precise_sleep(sleep_time);
        }
    }

    Py_END_ALLOW_THREADS

    running = false;
    Py_RETURN_NONE;
}

static PyObject* stop_game_loop(PyObject *self, PyObject *args) {
    running = false;
    Py_RETURN_NONE;
}

// Callback setters
static PyObject* set_update(PyObject *self, PyObject *args) {
    PyObject *temp;
    if (!PyArg_ParseTuple(args, "O", &temp) || !PyCallable_Check(temp)) {
        PyErr_SetString(PyExc_TypeError, "Update function must be callable");
        return NULL;
    }
    Py_XINCREF(temp);
    Py_XDECREF(update_callback);
    update_callback = temp;
    Py_RETURN_NONE;
}

static PyObject* set_render(PyObject *self, PyObject *args) {
    PyObject *temp;
    if (!PyArg_ParseTuple(args, "O", &temp) || !PyCallable_Check(temp)) {
        PyErr_SetString(PyExc_TypeError, "Render function must be callable");
        return NULL;
    }
    Py_XINCREF(temp);
    Py_XDECREF(render_callback);
    render_callback = temp;
    Py_RETURN_NONE;
}

static PyObject* set_fps(PyObject *self, PyObject *args) {
    if (!PyArg_ParseTuple(args, "d", &target_fps)) return NULL;
    Py_RETURN_NONE;
}

// Define methods and module setup
static PyMethodDef GameLoopMethods[] = {
    {"start", start_game_loop, METH_NOARGS, "Start the game loop"},
    {"stop", stop_game_loop, METH_NOARGS, "Stop the game loop"},
    {"set_update", set_update, METH_VARARGS, "Set the update function"},
    {"set_render", set_render, METH_VARARGS, "Set the render function"},
    {"set_fps", set_fps, METH_VARARGS, "Set the FPS"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef gameloopmodule = {
    PyModuleDef_HEAD_INIT,
    "miniloop",
    "Render cycle loop handler with multiprocessing",
    -1,
    GameLoopMethods
};

PyMODINIT_FUNC PyInit_miniloop(void) {
    return PyModule_Create(&gameloopmodule);
}

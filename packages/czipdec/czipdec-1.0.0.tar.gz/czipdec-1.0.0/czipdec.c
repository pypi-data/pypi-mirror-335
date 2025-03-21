/*
 * Copyright (c) 2015-2025, Wood
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without modification,
 * are permitted provided that the following conditions are met:
 *
 *     * Redistributions of source code must retain the above copyright notice,
 *       this list of conditions and the following disclaimer.
 *     * Redistributions in binary form must reproduce the above copyright notice,
 *       this list of conditions and the following disclaimer in the documentation
 *       and/or other materials provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
 * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 * WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
 * FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 * DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
 * SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
 * CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
 * OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 */

#define PY_Sint32_CLEAN
#include <Python.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define POLYNOMIAL 0xEDB88320

typedef uint8_t  byte;
typedef uint32_t uint;
typedef int32_t int32;
typedef uint16_t uint16;

typedef struct {
    uint key0;
    uint key1;
    uint key2;
} ZipDecrypter;

static uint CrcTable[256];

static void GenerateCrcTable() {
    for (uint i = 0; i < 256; i++) {
        uint crc = i;
        for (int j = 0; j < 8; j++) {
            if (crc & 1)
                crc = (crc >> 1) ^ POLYNOMIAL;
            else
                crc >>= 1;
        }
        CrcTable[i] = crc;
    }
}

static uint crc32(byte ch, uint crc) {
    return (crc >> 8) ^ CrcTable[(crc ^ ch) & 0xFF];
}

static void UpdateKeys(ZipDecrypter *zd, byte c) {
    zd->key0 = crc32(c, zd->key0);
    zd->key1 = zd->key1 + (zd->key0 & 0xFF);
    zd->key1 = zd->key1 * 134775813 + 1;
    zd->key2 = crc32(zd->key1 >> 24, zd->key2);
}

static void SetKeys(ZipDecrypter *zd, const char *password) {
    zd->key0 = 305419896;
    zd->key1 = 591751049;
    zd->key2 = 878082192;
    while (*password) {
        UpdateKeys(zd, (byte)*password);
        password++;
    }
}

static void decrypt(ZipDecrypter *zd, byte *data, int32 length) {
    for (int32 i = 0; i < length; i++) {
        uint16 k = zd->key2 | 2;
        data[i] ^= (k * (k ^ 1)) >> 8;
        UpdateKeys(zd, data[i]);
    }
}

static PyObject* py_decrypt(PyObject* self, PyObject* args) {
    Py_buffer password;
    Py_buffer data;

    if (!PyArg_ParseTuple(args, "y*y*", &password, &data)) {
        return NULL;
    }

    if (data.len < 12) {
        PyErr_SetString(PyExc_ValueError, "Data length must be at least 12 bytes");
        return NULL;
    }

    ZipDecrypter zd;
    GenerateCrcTable();
    SetKeys(&zd, (const char*)password.buf);
    decrypt(&zd, (byte*)data.buf, 12); // check
    decrypt(&zd, (byte*)data.buf + 12, data.len - 12);
    PyObject* result = PyBytes_FromStringAndSize((char*)data.buf + 12, data.len - 12);
    PyBuffer_Release(&data);
    return result;
}

static PyMethodDef CZipDecMethods[] = {
    {"decrypt", (PyCFunction)py_decrypt, METH_VARARGS, "Decrypt ZIP encrypted data"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef czipdecmodule = {
    PyModuleDef_HEAD_INIT,
    "czipdec",
    NULL,
    -1,
    CZipDecMethods
};

PyMODINIT_FUNC PyInit_czipdec(void) {
    return PyModule_Create(&czipdecmodule);
}

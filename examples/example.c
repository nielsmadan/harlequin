#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define MAX_BUFFER_SIZE 8192
#define VERSION_STRING  "1.0.3"

/* Structure for managing a read buffer with automatic resizing */
typedef struct {
    char   *data;
    size_t  length;
    size_t  capacity;
    bool    is_dynamic;
} Buffer;

static Buffer *buffer_create(size_t initial_capacity)
{
    Buffer *buf = malloc(sizeof(Buffer));
    if (!buf)
        return NULL;

    buf->data = calloc(initial_capacity, sizeof(char));
    if (!buf->data) {
        free(buf);
        return NULL;
    }

    buf->length = 0;
    buf->capacity = initial_capacity;
    buf->is_dynamic = true;
    return buf;
}

/*
 * Append data to the buffer, resizing if necessary.
 * Returns the number of bytes written, or -1 on error.
 */
static int buffer_append(Buffer *buf, const char *src, size_t count)
{
    if (!buf || !src || count == 0)
        return -1;

    while (buf->length + count > buf->capacity) {
        size_t new_cap = buf->capacity * 2;
        if (new_cap > MAX_BUFFER_SIZE) {
            fprintf(stderr, "Error: buffer exceeds maximum size (%d)\n",
                    MAX_BUFFER_SIZE);
            return -1;
        }
        char *new_data = realloc(buf->data, new_cap);
        if (!new_data)
            return -1;
        buf->data = new_data;
        buf->capacity = new_cap;
    }

    memcpy(buf->data + buf->length, src, count);
    buf->length += count;
    return (int)count;
}

static void buffer_free(Buffer *buf)
{
    if (buf) {
        free(buf->data);
        free(buf);
    }
}

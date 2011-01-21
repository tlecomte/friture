/* 
 This code times the OpenGL pixel transfer rate from the graphics card to main memory 
 using glReadPixels().  
 
 For each format and component storage type that it tests, it does NUM_READBACKS
 glReadPixels() calls in a row to a buffer.  It does not do any rendering.
 
 It tests pixel formats GL_RGB, GL_BGR, GL_RGBA, GL_BGRA, but it is trivial to
 add GL_RED, GL_GREEN, etc.
 
 It tests the standard component storage types GL_UNSIGNED_BYTE, GL_BYTE, 
 GL_UNSIGNED_SHORT, GL_SHORT, GL_UNSIGNED_INT, GL_INT, GL_FLOAT, 
 and the "packed" storage types
 GL_UNSIGNED_BYTE_3_3_2, GL_UNSIGNED_BYTE_2_3_3_REV, GL_UNSIGNED_SHORT_5_6_5,
 GL_UNSIGNED_SHORT_5_6_5_REV, GL_UNSIGNED_SHORT_4_4_4_4,
 GL_UNSIGNED_SHORT_4_4_4_4_REV, GL_UNSIGNED_SHORT_5_5_5_1,
 GL_UNSIGNED_SHORT_1_5_5_5_REV, GL_UNSIGNED_INT_8_8_8_8,
 GL_UNSIGNED_INT_8_8_8_8_REV, GL_UNSIGNED_INT_10_10_10_2, and
 GL_UNSIGNED_INT_2_10_10_10_REV.
 
 When it is all done, it will print out the fastest to slowest format/type 
 combinations by data transfer rate and pixel transfer rate.
 
 Note that the timing is done using wall clock time, so test this on an 
 otherwise-unloaded system.
 
 This code is in the public domain.
 
 Adrian Secord, May 2006.
*/

/*
 Compile with:
 gcc -std=c99 -l glut pixel_transfer_test.c -o pixel_transfer_test
*/

#include <sys/time.h>
#include <stdlib.h>
#include <assert.h>
#include <stdio.h>

#if defined(__GNUC__) && (defined(__APPLE_CPP__) || defined(__APPLE_CC__))
 #include <GLUT/glut.h>
#else
 #include <GL/glut.h>
#endif

/* Number of stabilizing rounds to wait before starting testing */
#define NUM_STABILIZING_ROUNDS 10

/* Number of readbacks in one trial */
#define NUM_READBACKS 100

/* Memory alignment of rows of pixels, in bytes. */
#define ALIGNMENT 4

static int screen_width = 0, screen_height = 0;
static int stabilizing_rounds = NUM_STABILIZING_ROUNDS;

/* An OpenGL pixel format */
typedef struct {
    GLenum format;
    unsigned num_comp;
    const char* desc;
} format_t;

#define NUM_FORMATS 4
static format_t formats[] = {
 /* { GL_RED,   1, "GL_RED"   },
    { GL_GREEN, 1, "GL_GREEN"   },
    { GL_BLUE,  1, "GL_BLUE"   },
    { GL_ALPHA, 1, "GL_ALPHA"   }, */
    { GL_RGB,   3, "GL_RGB"   },
    { GL_BGR,   3, "GL_BGR"   },
    { GL_RGBA,  4, "GL_RGBA"  },
    { GL_BGRA,  4, "GL_BGRA"  } 
};
static int cur_format = 0;

/* An OpenGL component storage type */
typedef struct {
    GLenum type;
    unsigned byte_size;
    int num_comp;
    const char* desc;
} type_t;

#define NUM_TYPES 19
static type_t types[] = {
    { GL_UNSIGNED_BYTE,               sizeof(GLubyte),  1, "GL_UNSIGNED_BYTE" },
    { GL_BYTE,                        sizeof(GLbyte),   1, "GL_BYTE" }, 
    { GL_UNSIGNED_SHORT,              sizeof(GLushort), 1, "GL_UNSIGNED_SHORT" },
    { GL_SHORT,                       sizeof(GLshort),  1, "GL_SHORT" },
    { GL_UNSIGNED_INT,                sizeof(GLuint),   1, "GL_UNSIGNED_INT" },
    { GL_INT,                         sizeof(GLint),    1, "GL_INT" },
    { GL_FLOAT,                       sizeof(GLfloat),  1, "GL_FLOAT" },
    { GL_UNSIGNED_BYTE_3_3_2,         sizeof(GLubyte),  3, "GL_UNSIGNED_BYTE_3_3_2" },
    { GL_UNSIGNED_BYTE_2_3_3_REV,     sizeof(GLubyte),  3, "GL_UNSIGNED_BYTE_2_3_3" },
    { GL_UNSIGNED_SHORT_5_6_5,        sizeof(GLushort), 3, "GL_UNSIGNED_SHORT_5_6_5" },   
    { GL_UNSIGNED_SHORT_5_6_5_REV,    sizeof(GLushort), 3, "GL_UNSIGNED_SHORT_5_6_5_REV" },            
    { GL_UNSIGNED_SHORT_4_4_4_4,      sizeof(GLushort), 4, "GL_UNSIGNED_SHORT_4_4_4_4" },
    { GL_UNSIGNED_SHORT_4_4_4_4_REV,  sizeof(GLushort), 4, "GL_UNSIGNED_SHORT_4_4_4_4_REV" },        
    { GL_UNSIGNED_SHORT_5_5_5_1,      sizeof(GLushort), 4, "GL_UNSIGNED_SHORT_5_5_5_1" },
    { GL_UNSIGNED_SHORT_1_5_5_5_REV,  sizeof(GLushort), 4, "GL_UNSIGNED_SHORT_5_5_5_1_REV" },          
    { GL_UNSIGNED_INT_8_8_8_8,        sizeof(GLuint),   4, "GL_UNSIGNED_INT_8_8_8_8" },
    { GL_UNSIGNED_INT_8_8_8_8_REV,    sizeof(GLuint),   4, "GL_UNSIGNED_INT_8_8_8_8_REV" },
    { GL_UNSIGNED_INT_10_10_10_2,     sizeof(GLuint),   4, "GL_UNSIGNED_INT_10_10_10_2" },
    { GL_UNSIGNED_INT_2_10_10_10_REV, sizeof(GLuint),   4, "GL_UNSIGNED_INT_2_10_10_10_REV" }
};
static int cur_type = 0;

/* A format/type result */
typedef struct {
    int type;
    int format;
    double rate, pixel_rate;
} result_t;
static result_t results[NUM_TYPES * NUM_FORMATS];

/* Return an aligned size in bytes. */
static unsigned align_size(const unsigned num_bytes, const unsigned align) {
    if (num_bytes % align != 0) 
        return num_bytes + (align - (num_bytes % align));  
    else 
        return num_bytes;
}

/* Reverse sort by data rate */
static int compare_data_rate(const void* a, const void* b) {
    const double x = ((result_t*) b)->rate - ((result_t*) a)->rate;
    if (x < 0)
        return -1;
    else if (x > 0)
        return 1;
    else 
        return 0;
}

/* Reverse sort by pixel rate */
static int compare_pixel_rate(const void* a, const void* b) {
    const double x = ((result_t*) b)->pixel_rate - ((result_t*) a)->pixel_rate;
    if (x < 0)
        return -1;
    else if (x > 0)
        return 1;
    else 
        return 0;
}

/* Test if a pixel format and a component storage type are compatible */
static int compatible(const format_t f, const type_t t) {
    /* Single-component types are always compatible */
    if (t.num_comp == 1) 
        return 1;
    
    /* These types are only compatible with GL_RGB */
    if (t.type == GL_UNSIGNED_BYTE_3_3_2  || t.type == GL_UNSIGNED_BYTE_2_3_3_REV ||
        t.type == GL_UNSIGNED_SHORT_5_6_5 || t.type == GL_UNSIGNED_SHORT_5_6_5_REV)
        return (f.format == GL_RGB);
    
    /* Else the number of components in the type have to match the number in the format */
    return (f.num_comp == t.num_comp);
}

void display(void) {
    struct timeval time1, time2;
    double total_time, rate, pixel_rate;
    const unsigned pixel_size = formats[cur_format].num_comp * types[cur_type].byte_size / types[cur_type].num_comp;
    const unsigned buf_size = align_size(screen_width * pixel_size, ALIGNMENT) * screen_height;
    unsigned char* buf = (unsigned char*) malloc(buf_size);
    assert(buf);

    if (stabilizing_rounds) {
        printf("Stabilizing round %i\n", stabilizing_rounds);
    }
    
    glPixelStorei(GL_PACK_ALIGNMENT, ALIGNMENT);
    gettimeofday(&time1, NULL);
    for (int i = 0; i < NUM_READBACKS; ++i) {
        glReadPixels(0, 0, screen_width, screen_height, formats[cur_format].format, types[cur_type].type, buf);
    }
    gettimeofday(&time2, NULL);

    total_time = (time2.tv_sec + 1e-6 * time2.tv_usec - time1.tv_sec - 1e-6 * time1.tv_usec);
    rate = 1e-6 * NUM_READBACKS * buf_size / total_time;
    pixel_rate = 1e-6 * NUM_READBACKS * screen_width * screen_height / total_time;
    
    if (stabilizing_rounds) {
        --stabilizing_rounds;
    } else {
        results[cur_type * NUM_FORMATS + cur_format].type = cur_type;
        results[cur_type * NUM_FORMATS + cur_format].format = cur_format;
        results[cur_type * NUM_FORMATS + cur_format].rate = rate;
        results[cur_type * NUM_FORMATS + cur_format].pixel_rate = pixel_rate;
        
        printf("%s %s %g MB/s %g Mp/s\n", 
               formats[cur_format].desc, types[cur_type].desc, rate, pixel_rate);
        
        /* Find the next type that is compatible with the current format */
        do {
            ++cur_type;
        } while (!compatible(formats[cur_format], types[cur_type]) && cur_type < NUM_TYPES);
        
        /* Go to the next type/format */
        if (cur_type == NUM_TYPES) {
            cur_type = 0;
            
            if (++cur_format == NUM_FORMATS) {
                
                printf("\nSorted by data rate:\n");
                qsort(results, NUM_FORMATS * NUM_TYPES, sizeof(result_t), compare_data_rate);
                for (int i = 0; i < NUM_FORMATS * NUM_TYPES; ++i) {
                    if (results[i].rate >= 0) 
                        printf("%s %s %g MB/s\n", 
                               formats[results[i].format].desc, 
                               types[results[i].type].desc, 
                               results[i].rate);
                }
                
                printf("\nSorted by pixel rate:\n");
                qsort(results, NUM_FORMATS * NUM_TYPES, sizeof(result_t), compare_pixel_rate);
                for (int i = 0; i < NUM_FORMATS * NUM_TYPES; ++i) {
                    if (results[i].rate >= 0) 
                        printf("%s %s %g Mp/s\n", 
                               formats[results[i].format].desc, 
                               types[results[i].type].desc, 
                               results[i].pixel_rate);
                }
                
                exit(0);
            }
        }
    }
    
    free(buf);
    
    glutReportErrors();
    glutPostRedisplay();
}

void reshape(int w, int h) {
    screen_width = w;
    screen_height = h;
    printf("Screen size %i x %i\n", w, h);
}

void keyboard(unsigned char key, int x, int y) {
    switch (key) {
        case 'q':
        case 27:        /* Escape */
            exit(0);
            break;

        default:
            break;
    }
    glutPostRedisplay();
}

int main(int argc, char** argv) {
    const GLubyte *name, *renderer, *version;
    
    for (int i = 0; i < NUM_FORMATS * NUM_TYPES; ++i)
        results[i].rate = -1.0;
    
    glutInit(&argc, argv);
    glutInitDisplayMode(GLUT_RGB | GLUT_ALPHA);
    glutInitWindowSize(640, 480);
    glutCreateWindow(argv[0]);

    name     =  glGetString(GL_VENDOR);
    renderer =  glGetString(GL_RENDERER);
    version  =  glGetString(GL_VERSION);

    printf("Vendor: %s\nRenderer: %s\nVersion: %s\n", name, renderer, version);
    printf("Memory alignment is %i\n", ALIGNMENT);

    glutReshapeFunc(reshape);
    glutDisplayFunc(display);
   
    glutKeyboardFunc(keyboard);
    glutMainLoop();
    return 0;
}

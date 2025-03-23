#ifndef __UTILS_WRAPPER
#define __UTILS_WRAPPER

#include "Python.h"

typedef struct {
  int width;
  int height;
} pdf_size;

pdf_size get_pdf_page_size(int pagenumber, char* filepath);
char* get_pdf_page(int pagenumber, char* filepath);
pdf_size get_pdf_page_size_for_display(int pagenumber, char* filepath, int screen_width);
char* get_pdf_page_for_display(int pagenumber, char* filepath, int screen_width);

#endif

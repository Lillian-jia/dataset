#include <stdio.h>
#include <stdlib.h>
#include <iostream>
#include <cstring>

/* Include files */
#include "apr_errno.h"
/* End */

#define ARG_NUM 1
#define SIZE 10240

int main(int argc, char **argv) {

    /* Read and data from afl's input */

    FILE* fp = fopen(argv[1], "r");
    if(!fp) {
        printf("Failed to open input file\n");
        exit(-1);
    }

    /* Init variables */
    int val_0 = 0;
    char * val_1 = (char * )malloc(SIZE);
    unsigned int val_2 = 0;
    /* End Init */

    /* Parse data */
    char buffer[SIZE];
    memset(buffer, 0, SIZE);
    char* left = 0, *right = 0;

    fgets(buffer, sizeof(buffer) - 1, fp);
    left = strchr(buffer, '=');
    if(left) {
        right = strchr(left + 1, '=');
        if(right) {
            sscanf(right + 1, "%d", &val_0);
            memset(buffer, 0, SIZE);
        }
    }

    fgets(buffer, sizeof(buffer) - 1, fp);
    left = strchr(buffer, '=');
    if(left) {
        right = strchr(left + 1, '=');
        if(right) {
            sscanf(right + 1, "%s", (char*)val_1);
            memset(buffer, 0, SIZE);
        }
    }

    fgets(buffer, sizeof(buffer) - 1, fp);
    left = strchr(buffer, '=');
    if(left) {
        right = strchr(left + 1, '=');
        if(right) {
            sscanf(right + 1, "%d", &val_2);
            memset(buffer, 0, SIZE);
        }
    }
    /* End Parse */

    fclose(fp);
    /* End */

    /* Call API */
    char * ret_0 = apr_strerror((int)val_0, (char *)val_1, (unsigned int)val_2);

    /* Well Done! */
    return 0;
}
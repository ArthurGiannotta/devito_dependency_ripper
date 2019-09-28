#include <stdio.h>
//INCLUDE_OPERATORS

// Allocates memory for the data used by the devito operator
void create_dataobj(struct dataobj* object, const char* filename)
{
    FILE* file = fopen(filename, "r");

    int size;
    fscanf(file, "%d ", &size);

    object->data = malloc(size * sizeof(float));

    int shape_size;
    fscanf(file, "%d", &shape_size);

    object->size = malloc(shape_size * sizeof(int));
    for (unsigned int i = 0; i < shape_size; ++i) {
        fscanf(file, " %d", &object->size[i]);
    }

    fflush(file);
    unsigned long pos = ftell(file) + 1;

    fclose(file);

    FILE* bfile = fopen(filename, "rb");

    fseek(file, pos, SEEK_SET);
    fread(object->data, size, sizeof(float), file);

    fclose(bfile);
}

// Frees memory for the data used by the devito operator
void destroy_dataobj(struct dataobj* object)
{
    free(object->data);
    free(object->size);
}

int main(int argc, char* argv[])
{
    // Initializes each variable
    //INIT_VARIABLES

    // Saves damp data in human readable format
    //SAVE_VARIABLE_TEXTMODE damp

    // Executes the operator
    //RUN_OPERATOR Kernel

    // Saves variables for future plotting in binary format
    //SAVE_VARIABLE_PLOTMODE u
    //SAVE_VARIABLE_PLOTMODE rec

    // Frees memory for allocated variables
    //FREE_VARIABLES

    return 0;
}

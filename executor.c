#include <stdio.h>
#include "operators/Kernel/operator.h"

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
    FILE* plot_file;

    const float dt = 1.68;
    const float o_x = -100.0;
    const float o_y = -100.0;
    const int x_M = 120;
    const int x_m = 0;
    const int y_M = 120;
    const int y_m = 0;
    const int p_rec_M = 100;
    const int p_rec_m = 0;
    const int p_src_M = 0;
    const int p_src_m = 0;
    const int time_M = 1191;
    const int time_m = 1;

    struct profiler * timers = malloc(sizeof(struct profiler));

    struct dataobj * damp = malloc(sizeof(struct dataobj));
    create_dataobj(damp, "dataobjs/damp.dataobj");

    struct dataobj * rec = malloc(sizeof(struct dataobj));
    create_dataobj(rec, "dataobjs/rec.dataobj");

    struct dataobj * rec_coords = malloc(sizeof(struct dataobj));
    create_dataobj(rec_coords, "dataobjs/rec_coords.dataobj");

    struct dataobj * src = malloc(sizeof(struct dataobj));
    create_dataobj(src, "dataobjs/src.dataobj");

    struct dataobj * src_coords = malloc(sizeof(struct dataobj));
    create_dataobj(src_coords, "dataobjs/src_coords.dataobj");

    struct dataobj * u = malloc(sizeof(struct dataobj));
    create_dataobj(u, "dataobjs/u.dataobj");

    struct dataobj * vp = malloc(sizeof(struct dataobj));
    create_dataobj(vp, "dataobjs/vp.dataobj");

    // Saves damp data in human readable format
    if (plot_file = fopen("saves/damp.save", "w")) {;
    	fprintf(plot_file, "123 123\n");

    	for (unsigned int i0 = 0; i0 < 123; ++i0) {
	    	for (unsigned int i1 = 0; i1 < 123; ++i1) {
		    	float (*restrict damp_temp__)[damp->size[1]] __attribute__ ((aligned (64))) = (float (*)[damp->size[1]]) damp->data;
		    	fprintf(plot_file, "%f", damp_temp__[i0][i1]);
		    }
	    }

    	fclose(plot_file);
    	plot_file = NULL;
    }

    // Executes the operator
    Kernel(damp, dt, o_x, o_y, rec, rec_coords, src, src_coords, u, vp, x_M, x_m, y_M, y_m, p_rec_M, p_rec_m, p_src_M, p_src_m, time_M, time_m, timers);

    // Saves variables for future plotting in binary format
    if (plot_file = fopen("saves/u.save", "w")) {;
    	fprintf(plot_file, "1193 125 125\n");

    	fwrite(u->data, sizeof(float), 18640625, plot_file);

    	fclose(plot_file);
    	plot_file = NULL;
    }
    if (plot_file = fopen("saves/rec.save", "w")) {;
    	fprintf(plot_file, "1192 101\n");

    	fwrite(rec->data, sizeof(float), 120392, plot_file);

    	fclose(plot_file);
    	plot_file = NULL;
    }

    // Frees memory for allocated variables
    free(timers);

    destroy_dataobj(damp);
    free(damp);

    destroy_dataobj(rec);
    free(rec);

    destroy_dataobj(rec_coords);
    free(rec_coords);

    destroy_dataobj(src);
    free(src);

    destroy_dataobj(src_coords);
    free(src_coords);

    destroy_dataobj(u);
    free(u);

    destroy_dataobj(vp);
    free(vp);

    return 0;
}

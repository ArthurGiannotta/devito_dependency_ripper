import os
import shutil
import sys

executor = "executor.c"          # Name of the executor C file to be generated
executable = "operator.bin"      # Name of the binary file to be compiled and run
template = "executor_template.c" # Name of the C file to be used as template

try:
    execute_operator = sys.argv[1] == "-run"
except:
    execute_operator = False

try:
    skip_operators = sys.argv[1] == "-skip"
except:
    skip_operators = False

if execute_operator:
    if os.path.isdir("saves"):
        shutil.rmtree("saves")
    
    os.mkdir("saves")

    os.system("gcc " + executor + " -std=c99 -lm -g -o " + executable)
    os.system("./" + executable)
else:
    if not skip_operators:
        # Remove old directories and files
        if os.path.exists("operators.txt"):
            os.remove("operators.txt")

        if os.path.isdir("operators"):
            shutil.rmtree("operators")

        if os.path.isdir("dataobjs"):
            shutil.rmtree("dataobjs")

        import operators as ops

    if os.path.exists("plot_parameters.txt"):
        os.remove("plot_parameters.txt")

    operators = dict()
    with open("operators.txt") as operators_file:
        for line in operators_file:
            operators[line.strip()] = []

    variables = dict()
    for operator, args in operators.items():
        with open("operators/" + operator + "/variables.txt", "r") as variables_file:
            i = 0
            for line in variables_file:
                i += 1

                line = line.strip()

                if i % 3 == 1:
                    name = line
                elif i % 3 == 2:
                    ty = line
                else:
                    value = line
                    args.append([name, ty, value])

                    if name in variables.keys():
                        if variables[name] != [ty, value]:
                            raise Exception("Two variables with same name and different types or values")
                    else:
                        variables[name] = [ty, value]

                        if name == "dt":
                            with open("plot_parameters.txt", "a") as plot_parameters:
                                plot_parameters.write(name + "\n" + str(value) + "\n")
    
    dataobjs = []
    profiler = None
    with open(template, "r") as template_file:
        with open(executor, "w") as executor_file:
            for line in template_file:
                if "//INCLUDE_OPERATOR" in line:
                    tabulation = line[0:line.find("//")]

                    name = line[line.find("//") + len("//INCLUDE_OPERATOR "):].strip()
                    executor_file.write(tabulation + "#include \"operators/" + name + "/operator.h\"\n")
                elif "//INIT_VARIABLES" in line:
                    tabulation = line[0:line.find("//")]

                    executor_file.write(tabulation + "FILE* plot_file;\n\n")

                    for name, variable in variables.items():
                        ty, value = variable[0], variable[1]

                        if "const" in ty:
                            executor_file.write(tabulation + ty + " " + name + " = " + value + ";\n")
                        elif "dataobj" in ty:
                            dataobjs += [[name, ty, value]]
                        elif "profiler" in ty:
                            profiler = name
                            executor_file.write("\n" + tabulation + ty + " " + name + " = malloc(sizeof(struct profiler));\n")
                        else:
                            executor_file.write(tabulation + ty + " " + name + ";\n")
                    
                    for dataobj in dataobjs:
                        name, ty, value = dataobj[0], dataobj[1], dataobj[2]

                        executor_file.write("\n" + tabulation + ty + " " + name + " = malloc(sizeof(struct dataobj));\n")
                        executor_file.write(tabulation + "create_dataobj(" + name + ", \"dataobjs/" + value + "\");\n")
                elif "//RUN_OPERATOR" in line:
                    tabulation = line[0:line.find("//")]

                    name = line[line.find("//") + len("//RUN_OPERATOR "):].strip()
                    try:
                        arguments = operators[name]

                        executor_file.write(tabulation + name + "(")
                        for arg in arguments[0:-1]:
                            executor_file.write(arg[0] + ", ")
                        executor_file.write(arguments[-1][0] + ");\n")  
                    except:
                        raise Exception("Invalid operator name \"" + name + "\"")
                elif "//SAVE_VARIABLE" in line:
                    tabulation = line[0:line.find("//")]

                    name = line[line.find("//") + len("//SAVE_VARIABLE_XXXXMODE "):].strip()
                    dataobj_path = "dataobjs/" + name + ".dataobj"

                    if os.path.exists(dataobj_path):
                        with open(dataobj_path, "rb") as dataobj_file:
                            data = dataobj_file.readline().decode("utf-8").strip().split(" ")
                            size, dims, shape = data[0], data[1], data[2:]

                        executor_file.write(tabulation + "if (plot_file = fopen(\"saves/" + name + ".save\", \"w\")) {;\n")
                        executor_file.write(tabulation + "\tfprintf(plot_file, \"" + " ".join([str(v) for v in shape]) + "\\n\");\n\n")

                        if "//SAVE_VARIABLE_TEXTMODE" in line:
                            i = 0
                            for dim in shape:
                                for j in range(i):
                                    executor_file.write("\t")

                                executor_file.write(tabulation + "\tfor (unsigned int i" + str(i) + " = 0; i" + str(i) + " < " + str(dim) + "; ++i" + str(i) + ") {\n")

                                i += 1

                            for j in range(i):
                                executor_file.write("\t")
                            indexes = "][".join([name + "->size[" + str(j) + "]" for j in range(1, i)])
                            executor_file.write(tabulation + "\tfloat (*restrict " + name + "_temp__)[" + indexes + "] __attribute__ ((aligned (64))) = (float (*)[" + indexes + "]) " + name + "->data;\n")
                            
                            for j in range(i):
                                executor_file.write("\t")
                            executor_file.write(tabulation + "\tfprintf(plot_file, \"%f\", " + name + "_temp__[" + "][".join(["i" + str(j) for j in range(i)]) + "]);\n")
                            
                            for dim in shape:
                                for j in range(i):
                                    executor_file.write("\t")

                                executor_file.write(tabulation + "}\n")

                                i -= 1
                        elif "//SAVE_VARIABLE_PLOTMODE" in line:
                            executor_file.write(tabulation + "\tfwrite(" + name + "->data, sizeof(float), " + size + ", plot_file);\n")
                        
                        executor_file.write("\n" + tabulation + "\tfclose(plot_file);\n")
                        executor_file.write(tabulation + "\tplot_file = NULL;\n")
                        executor_file.write(tabulation + "}\n")
                    else:
                        Exception("Invalid save variable (should be a dataobj)")

                elif "//FREE_VARIABLES" in line:
                    tabulation = line[0:line.find("//")]

                    if profiler is not None:
                        executor_file.write(tabulation + "free(" + profiler + ");\n")

                    for dataobj in dataobjs:
                        name = dataobj[0]

                        executor_file.write("\n" + tabulation + "destroy_dataobj(" + name + ");\n")
                        executor_file.write(tabulation + "free(" + name + ");\n")
                else:
                    executor_file.write(line)

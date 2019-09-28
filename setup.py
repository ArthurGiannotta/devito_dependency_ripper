import devito.operator
import devito.types.dense
import os
import sys

try:
    restore = sys.argv[1] == "-restore"
except:
    restore = False

# Gets the paths of the files to be modified
operator_path = devito.operator.__file__
dense_path = devito.types.dense.__file__

operator_backup_path = operator_path + "_backup"
dense_backup_path = dense_path + "_backup"

if restore:
    def restore_file(path, backup_path):
        if not os.path.exists(backup_path):
            print("\"" + path + 
                "\" has not been modified, please check since there is no backup file \"" + 
                backup_path + "\"")
        else:
            with open(backup_path, "r") as backup:
                with open(path, "w") as file:
                    for line in backup:
                        file.write(line)
            os.remove(backup_path)

    restore_file(operator_path, operator_backup_path)
    restore_file(dense_path, dense_backup_path)
else:
    def make_backup(path, backup_path):
        with open(path, "r") as file:
            with open(backup_path, "w") as backup:
                for line in file:
                    backup.write(line)
    
    operator_extra_code = """
            import os

            if not os.path.isdir("operators"):
                os.mkdir("operators")

            operator_folder = "operators/" + self.name
            if os.path.isdir(operator_folder):
                operator_folder += "_"
                self.name += "_"
                # raise InvalidOperator("There already exists an operator with this name. Try passing \\"name=\\'ExampleOperator\\'\\" as argument for Operator().")

            os.mkdir(operator_folder)

            with open("operators.txt", "a") as operators:
                operators.write(self.name + "\\n")

            variables = open(operator_folder + "/variables.txt", "w")

            for p in self.parameters:
                arg = args[p.name]

                variables.write(p.name + "\\n" + p._C_typename + "\\n")

                if hasattr(arg, "_obj"):
                    variables.write(p.name + ".dataobj\\n")
                else:
                    variables.write(str(arg) + "\\n")

            variables.close()

            with open("operators/" + self.name + "/operator.h", "w") as operator_file:
                operator_file.write(str(self.ccode))
"""

    dense_extra_code = """
        import os
        
        if not os.path.isdir("dataobjs"):
            os.mkdir("dataobjs")

        data_file = open("dataobjs/" + self.name + ".dataobj", "w")

        data_file.write(str(data.size) + " " + str(len(data.shape)))

        for dim in data.shape:
            data_file.write(" " + str(dim))

        data_file.write("\\n")

        data.tofile(data_file)

        data_file.close()
"""

    if os.path.exists(operator_backup_path):
        print("\"" + operator_path + 
        "\" has already been modified, please restore the backup file \"" + 
        operator_backup_path + "\" if you want to redo the setup")
    else:
        make_backup(operator_path, operator_backup_path)
        with open(operator_backup_path, "r") as backup:
            with open(operator_path, "w") as file:
                for line in backup:
                    if "self.cfunction" in line:
                        file.write(operator_extra_code)
                    else:
                        file.write(line)
        
    if os.path.exists(dense_backup_path):
        print("\"" + dense_path + 
        "\" has already been modified, please restore the backup file \"" + 
        dense_backup_path + "\" if you want to redo the setup")
    else:
        make_backup(dense_path, dense_backup_path)
        with open(dense_backup_path, "r") as backup:
            with open(dense_path, "w") as file:
                for line in backup:
                    if "dataobj._obj.data = data.ctypes.data_as(c_void_p)" in line:
                        file.write(line)
                        file.write(dense_extra_code)
                    else:
                        file.write(line)

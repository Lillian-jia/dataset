import os

import yaml
from yaml.loader import SafeLoader

supported_type = [
    "void",
    "void*",
    "char",
    "unsigned char",
    "char*",
    "char *",
    "unsigned char*",
    "unsigned char *",
    "short",
    "unsigned short",
    "short*",
    "short *",
    "unsigned short*",
    "unsigned short *",
    "int",
    "unsigned int",
    "int*",
    "int *",
    "unsigned int*",
    "unsigned int *",
    "long",
    "unsigned long",
    "long*",
    "long *",
    "unsigned long*",
    "unsigned long *",
    "long long",
    "long long*",
    "long long *",
    "float",
    "double",
]

type_format = {
    "void*": "%s",
    "char": "%c",
    "unsigned char": "%c",
    "char*": "%s",
    "char *": "%s",
    "unsigned char*": "%s",
    "unsigned char *": "%s",
    "short": "%hd",
    # "short*":,
    # "short *",
    "int": "%d",
    "unsigned int": "%d",
    # "int*",
    # "int *",
    "long": "%ld",
    # "long*",
    # "long *",
    "long long": "%lld",
    # "long long*",
    # "long long *",
    "float": "%f",
    "double": "%lf",
}


def parse_fun_sig(signature: str):
    i = j = signature.find('(') - 1
    while i >= 0 and signature[i] != ' ':
        i -= 1
    returnType = signature[0:i].strip()
    funcName = signature[i + 1:j + 1].strip()
    argTypes = list()

    arg_str = signature[j + 2:signature.find(')')].strip().split(',')
    if len(arg_str) == 1 and arg_str[0] == '':
        argTypes.append("void")
        arg_str = []
    for item in arg_str:
        is_supported = False
        for s_type in supported_type:
            if s_type in item.strip():
                is_supported = True
                break
        if not is_supported:
            raise Exception(f"Unsupported Type: {item}")
        if item.strip() == 'void' and len(arg_str) != 1:
            raise Exception("Confused in void")
        argTypes.append(item.strip())
    return returnType, funcName, argTypes


def generate_harness(info_file, dir):
    # info_file = "libguac_string_strlcpy.yaml"
    with open(info_file, 'r') as fp:
        info_data = yaml.load(fp, Loader=SafeLoader)

    lib_name = list(info_data.keys())[0]
    fun_list = info_data[lib_name]

    total_fun = 0
    fun_args = []
    fun_names = []
    fun_rets = []

    header_files = set()
    for i in range(len(fun_list)):
        # print(fun_list[i])
        fun_name = list(fun_list[i].keys())[0]
        fun_val = fun_list[i][fun_name]

        assert isinstance(fun_val['headers'], list)
        for header_file in fun_val['headers']:
            header_files.add(header_file)

        assert isinstance(fun_val['signature'], str)
        sig = fun_val['signature']
        if 'file_arg' in fun_val.keys():
            file_arg = fun_val['file_arg']
        ret, fun_n, args = parse_fun_sig(sig)
        fun_args.append(args)
        fun_rets.append(ret)
        fun_names.append(fun_n)
        total_fun += 1

    # print(header_files)
    print(fun_names, fun_rets, fun_args)

    harness_content = "#include <stdio.h>\n" \
                      "#include <stdlib.h>\n" \
                      "#include <iostream>\n" \
                      "#include <cstring>\n" \
                      "\n" \
                      "/* Include files */\n"

    for header in header_files:
        harness_content = harness_content + f"#include \"{header}\"\n"
    harness_content += "/* End */\n\n" \
                       f"#define ARG_NUM {total_fun}\n" \
                       f"#define SIZE {10240}\n\n" \
                       "int main(int argc, char **argv) {\n\n" \
                       "    /* Read and data from afl's input */\n\n" \
                       "    FILE* fp = fopen(argv[1], \"r\");\n" \
                       "    if(!fp) {\n" \
                       "        printf(\"Failed to open input file\\n\");\n" \
                       "        exit(-1);\n" \
                       "    }\n\n" \
                       "    /* Init variables */\n"

    # Init variables here
    var_idx = 0
    var_vector = []
    for args in fun_args:
        tmp = {}
        for arg_type in args:
            if arg_type == 'void':
                break
            arg_type = arg_type.strip()
            var_name = f"val_{var_idx}"
            tmp[var_name] = arg_type
            var_idx += 1

            if '*' in arg_type:
                # pointer
                '''
                if arg_type == 'void*' or arg_type == 'void *':
                    harness_content += f"    {arg_type} {var_name} = 0;\n"
                else:
                    harness_content += f"    {arg_type} {var_name} = ({arg_type} )malloc(SIZE);\n"
                '''
                harness_content += f"    {arg_type} {var_name} = ({arg_type} )malloc(SIZE);\n"
            else:
                # basic variable type
                harness_content += "    " + arg_type + " " + var_name + " = 0;\n"

        var_vector.append(tmp)

    harness_content += "    /* End Init */\n\n" \
                       "    /* Parse data */\n" \
                       "    char buffer[SIZE];\n" \
                       "    memset(buffer, 0, SIZE);\n" \
                       "    char* left = 0, *right = 0;\n"

    print(var_vector)
    for vector in var_vector:
        if len(vector) == 0:
            continue
        for val_name, type in vector.items():
            harness_content += "\n    fgets(buffer, sizeof(buffer) - 1, fp);\n" \
                               "    left = strchr(buffer, '=');\n" \
                               "    if(left) {\n" \
                               "        right = strchr(left + 1, '=');\n" \
                               "        if(right) {\n"
            if '*' in type:
                # pointer
                harness_content += f"            sscanf(right + 1, \"%s\", (char*){val_name});\n"
            else:
                harness_content += f"            sscanf(right + 1, \"{type_format[type]}\", &{val_name});\n"

            harness_content += "            memset(buffer, 0, SIZE);\n" \
                               "        }\n" \
                               "    }\n"
    harness_content += "    /* End Parse */\n\n    fclose(fp);\n    /* End */\n\n"

    harness_content += '    /* Call API */\n'
    ret_idx = 0
    for i in range(total_fun):
        if fun_rets[i] != 'void':
            harness_content += f"    {fun_rets[i]} ret_{ret_idx} = "
            ret_idx += 1
        else:
            harness_content += f"    "

        harness_content += f"{fun_names[i]}("
        for val_n, type in var_vector[i].items():
            harness_content += f"({type}){val_n}, "
        if len(var_vector[i]) != 0:
            harness_content = harness_content[:-2]
        harness_content += ");\n"

    harness_content += "\n    /* Well Done! */\n" \
                       "    return 0;\n}"

    print(harness_content)

    output_file = lib_name + "_"
    for fun_name in fun_names:
        output_file += fun_name.replace('::', '_')
        output_file += '_'
    output_file = output_file[:-1] + '.cpp'
    output_file = os.path.join(dir, output_file)

    with open(output_file, "w+") as fp:
        fp.write(harness_content)

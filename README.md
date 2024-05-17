# HOW TO RUN

## Prerequisites

1. You need to have Python3 installed on your machine.

## Steps

1. Extract the contents of the zipped folder onto your machine.
2. Either copy the input file containing the RPAL expression into the folder, or enter the program into the
   ”input file.txt” file. The file containing the RPAL program must be directly under the PROJECT-CS3513
   folder.
3. You can either run the python file directly from the command line, or you can use a make command.
   (a) To use the terminal :
   i. Open a terminal in the Project-CS3513 directory, and run the following command :
   python ./myrpal.py <name of file containing RPAL expression>
   This will run the RPAL program. If a Print is called in the RPAL program, the printed value will be
   displayed on the console.
   ii. If you want to print the AST (Abstract Syntax Tree), you need to add a ’-ast’ flag to the above
   command. Keep in mind that this will only print the AST for the program, and the program will not
   actually execute. The new terminal command will look like :
   `bash
   python ./myrpal.py <name of file containing RPAL expression> -ast
   `
   (b) To use the make command :
   i. Open a terminal in the Project-CS3513 directory, and run the following command :
   `bash
   make run filename="<whatever_the_file_name_is>.txt"
   `
   This will run the RPAL program. If a Print is called in the RPAL program, the printed value will be
   displayed on the console.
   ii. If you want to print the AST (Abstract Syntax Tree), you need to use a different target: ast The new
   terminal command will look like :
   `bash
   make ast filename="<whatever_the_file_name_is>.txt"
   `

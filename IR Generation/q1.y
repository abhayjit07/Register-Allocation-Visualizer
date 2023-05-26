%{
    #include <stdio.h>
    #include <string.h>

    int countline = 1;
    int countvar = 0;
    char ir[2000];
    int stack[100];
    int ifstack[100];
    int top = 0;
    int iftop = 0;

    extern FILE* yyin;
%}

%union{
    char str[2000];
}

%token END
%token ID NUM WHILE LE GE EQ NE OR AND OP CP DO PRINT IF ELSE
%right '='
%left AND OR
%left '<' '>' LE GE EQ NE
%left '+''-'
%left '*''/' '%'
%left '!'
%right UMINUS

%type <str> EXPRN
%type <str> EXPRNS
%type <str> WBCK
%type <str> CODE
%type <str> S
%type <str> BODY
%type <str> IFSTMNT
%type <str> IFBCK
%type <str> IFBDY
%type <str> WSTMNT
%type <str> NUM
%type <str> ID

%%

S : CODE END {
sprintf(ir, "%s", $1);
return 0;}
        ;

CODE: WBCK {
    sprintf($$, "%s", $1);
}
            | IFBCK {
    sprintf($$, "%s", $1);
}
            | EXPRNS ';' {
    sprintf($$, "%s", $1);
}
            | CODE CODE {
    sprintf($$, "%s\n%s", $1, $2);
}
            ;

WBCK: WSTMNT '{' BODY '}' {
    sprintf($$, "%s (%d)\n%s\ngoto (%d)", $1, countline + 1, $3, stack[--top]);
    countline++;
}
        | WSTMNT ';' {
    sprintf($$, "%s (%d)\ngoto %d", $1, countline + 1, stack[--top]);
    countline++;
}
        | WSTMNT EXPRN ';' {
    sprintf($$, "%s (%d)\n%s\ngoto (%d)", $1, countline + 1, ir, stack[--top]);
    sprintf(ir, "\0");
    countline++;
}
        | WSTMNT WBCK {
    sprintf($$, "%s (%d)\n%s\ngoto (%d)", $1, countline + 1, $2, stack[--top]);
    countline++;
}
        | WSTMNT IFBCK {
    sprintf($$, "%s (%d)\n%s\ngoto (%d)", $1, countline + 1, $2, stack[--top]);
    countline++;
}
        | WSTMNT '{' '}' {
    sprintf($$, "%s (%d)\ngoto (%d)", $1, countline + 1, stack[--top]);
}
        ;

WSTMNT: WHILE OP EXPRN CP {
    int irStartLine = countline - 1;
    for(int i = 0; i < strlen(ir); i++)
    {
        if(ir[i] == '\n')
        {
            irStartLine--;
        }
    }
    if(ir[0] == '\0') irStartLine = countline;
    sprintf($$, "%s\n%s = %s == 0\nif %s goto", ir, $3, $3, $3);
    sprintf(ir, "\0");
    if($$[0] == '\n')
    {
        for(int i = 0; i < strlen($$); i++)
        {
            $$[i] = $$[i + 1];
        }
    }
    stack[top] = irStartLine;
    top++;
    countline = countline + 2;
}
                ;

EXPRNS: EXPRN {
    $$[0] = '\0';
    sprintf($$, "%s", ir);
    sprintf(ir, "\0");
}
        |PRINT EXPRN {
    sprintf($$, "print (%s)", $2);
    countline++;
}
        |EXPRNS ';' EXPRN {
    sprintf($$, "%s\n%s", $1, ir);  
    sprintf(ir, "\0");  
}
        |EXPRNS ';' PRINT EXPRN {
    sprintf($$, "%s\n%sprint (%s)", $1, ir, $4);
    sprintf(ir, "\0"); 
    countline++;
}
        ;

IFSTMNT: IF OP EXPRN CP {
    int irStartLine = countline - 1;
    for(int i = 0; i < strlen(ir); i++)
    {
        if(ir[i] == '\n')
        {
            irStartLine--;
        }
    }
    if(ir[0] == '\0') irStartLine = countline;
    sprintf($$, "%s\n%s = %s == 0\nif %s goto", ir, $3, $3, $3);
    sprintf(ir, "\0");
    if($$[0] == '\n')
    {
        for(int i = 0; i < strlen($$); i++)
        {
            $$[i] = $$[i + 1];
        }
    }
    countline = countline + 2;
}
        ;

IFBCK: IFSTMNT IFBDY {
    sprintf($$, "%s (%d)\n%s (%d)", $1, countline + 1, $2, countline);
    top--;
}
        | IFSTMNT IFBDY ELSE IFBDY {
        int elseend = ifstack[--top];
        int ifend = ifstack[--top];
        sprintf($$, "%s (%d)\n%s (%d)\n%s (%d)", $1, ifend, $2, elseend, $4, countline);
}
        ;

IFBDY: '{' BODY '}' {
    sprintf($$, "%s\ngoto", $2);
    ifstack[top] = ++countline;
    top++;
}
    | EXPRN ';' {
    sprintf($$, "%s\ngoto", ir);
    sprintf(ir, "\0");
    ifstack[top] = ++countline;
    top++;
}
    | IFBCK {
    sprintf($$, "%s\ngoto", $1);
    ifstack[top] = ++countline;
    top++;
}
    | WBCK {
    sprintf($$, "%s\ngoto", $1);
    ifstack[top] = ++countline;
    top++;
}
    | '{' '}' {
    sprintf($$, "goto");  
    ifstack[top] = ++countline;
    top++;
}

BODY: WBCK {
    sprintf($$, "%s", $1);
}
        |EXPRNS ';' {
    sprintf($$, "%s", $1);
}
        |IFBCK {
    sprintf($$, "%s", $1);
}
        |BODY BODY {
    sprintf($$, "%s\n%s", $1, $2);
}
        ;
        

EXPRN: EXPRN '+' EXPRN {
    sprintf(ir, "%s\nt%d = %s + %s", ir, countvar, $1, $3);
    $$[0] = '\0';
    sprintf($$, "t%d", countvar);
    if(ir[0] == '\n')
    {
        for(int i = 0; i < strlen(ir); i++)
        {
            ir[i] = ir[i + 1];
        }
    }
    countvar++;
    countline++;
}
        |'-' EXPRN %prec UMINUS {
    sprintf(ir, "%s\nt%d = uminus %s", ir, countvar, $2);
    $$[0] = '\0';
    sprintf($$, "t%d", countvar);
    countvar++;
    if(ir[0] == '\n')
    {
        for(int i = 0; i < strlen(ir); i++)
        {
            ir[i] = ir[i+1];
        }
    }
    countline++;
}
        |EXPRN '*' EXPRN {
    sprintf(ir, "%s\nt%d = %s * %s", ir, countvar, $1, $3);
    $$[0] = '\0';
    sprintf($$, "t%d", countvar);
    if(ir[0] == '\n')
    {
        for(int i = 0; i < strlen(ir); i++)
        {
            ir[i] = ir[i + 1];
        }
    }
    countvar++;
    countline++;
}
        |EXPRN '-' EXPRN {
    sprintf(ir, "%s\nt%d = %s - %s", ir, countvar, $1, $3);
    $$[0] = '\0';
    sprintf($$, "t%d", countvar);
    countvar++;
    if(ir[0] == '\n')
    {
        for(int i = 0; i < strlen(ir); i++)
        {
            ir[i] = ir[i + 1];
        }
    }
    countline++;
}
        |EXPRN '/' EXPRN {
    sprintf(ir, "%s\nt%d = %s / %s", ir, countvar, $1, $3);
    $$[0] = '\0';
    sprintf($$, "t%d", countvar);
    if(ir[0] == '\n')
    {
        for(int i = 0; i < strlen(ir); i++)
        {
            ir[i] = ir[i + 1];
        }
    }
    countvar++;
    countline++;
}
        |EXPRN '%' EXPRN {
    sprintf(ir, "%s\nt%d = %s %% %s", ir, countvar, $1, $3);
    $$[0] = '\0';
    sprintf($$, "t%d", countvar);
    if(ir[0] == '\n')
    {
        for(int i = 0; i < strlen(ir); i++)
        {
            ir[i] = ir[i + 1];
        }
    }
    countvar++;
    countline++;
}
        |EXPRN '<' EXPRN {
    sprintf(ir, "%s\nt%d = %s < %s", ir, countvar, $1, $3);
    $$[0] = '\0';
    sprintf($$, "t%d", countvar);
    if(ir[0] == '\n')
    {
        for(int i = 0; i < strlen(ir); i++)
        {
            ir[i] = ir[i + 1];
        }
    }
    countvar++;
    countline++;
}
        |EXPRN '>' EXPRN {
    sprintf(ir, "%s\nt%d = %s > %s", ir, countvar, $1, $3);
    $$[0] = '\0';
    sprintf($$, "t%d", countvar);
    if(ir[0] == '\n')
    {
        for(int i = 0; i < strlen(ir); i++)
        {
            ir[i] = ir[i + 1];
        }
    }
    countvar++;
    countline++;
}
        |EXPRN '=' EXPRN {
    sprintf(ir, "%s\n%s = %s", ir, $1, $3);
    $$[0] = '\0';
    sprintf($$, "%s", $1);
    if(ir[0] == '\n')
    {
        for(int i = 0; i < strlen(ir); i++)
        {
            ir[i] = ir[i + 1];
        }
    }
    countline++;
}
        |EXPRN OR EXPRN {
    sprintf(ir, "%s\nt%d = %s or %s", ir, countvar, $1, $3);
    $$[0] = '\0';
    sprintf($$, "t%d", countvar);
    if(ir[0] == '\n')
    {
        for(int i = 0; i < strlen(ir); i++)
        {
            ir[i] = ir[i + 1];
        }
    }
    countvar++;
    countline++;
}
        |EXPRN AND EXPRN {
    sprintf(ir, "%s\nt%d = %s and %s", ir, countvar, $1, $3);
    $$[0] = '\0';
    sprintf($$, "t%d", countvar);
    if(ir[0] == '\n')
    {
        for(int i = 0; i < strlen(ir); i++)
        {
            ir[i] = ir[i + 1];
        }
    }
    countvar++;
    countline++;
}
        |'!' EXPRN {
    sprintf(ir, "%s\nt%d = !%s", ir, countvar, $2);
    $$[0] = '\0';
    sprintf($$, "t%d", countvar);
    if(ir[0] == '\n')
    {
        for(int i = 0; i < strlen(ir); i++)
        {
            ir[i] = ir[i + 1];
        }
    }
    countvar++;
    countline++;
}
        |EXPRN GE EXPRN {
    sprintf(ir, "%s\nt%d = %s >= %s", ir, countvar, $1, $3);
    $$[0] = '\0';
    sprintf($$, "t%d", countvar);
    if(ir[0] == '\n')
    {
        for(int i = 0; i < strlen(ir); i++)
        {
            ir[i] = ir[i + 1];
        }
    }
    countvar++;
    countline++;
}
        |EXPRN EQ EXPRN {
    sprintf(ir, "%s\nt%d = %s == %s", ir, countvar, $1, $3);
    $$[0] = '\0';
    sprintf($$, "t%d", countvar);
    if(ir[0] == '\n')
    {
        for(int i = 0; i < strlen(ir); i++)
        {
            ir[i] = ir[i + 1];
        }
    }
    countvar++;
    countline++;
}
        |EXPRN NE EXPRN {
    sprintf(ir, "%s\nt%d = %s != %s", ir, countvar, $1, $3);
    $$[0] = '\0';
    sprintf($$, "t%d", countvar);
    if(ir[0] == '\n')
    {
        for(int i = 0; i < strlen(ir); i++)
        {
            ir[i] = ir[i + 1];
        }
    }
    countvar++;
    countline++;
}
        |EXPRN LE EXPRN {
    sprintf(ir, "%s\nt%d = %s <= %s", ir, countvar, $1, $3);
    $$[0] = '\0';
    sprintf($$, "t%d", countvar);
    if(ir[0] == '\n')
    {
        for(int i = 0; i < strlen(ir); i++)
        {
            ir[i] = ir[i + 1];
        }
    }
    countvar++;
    countline++;
}
        |OP EXPRN CP {
    $$[0] = '\0';
    sprintf($$, "%s", $2);
}
        |NUM {
    sprintf($$, "%s", $1);
}
        |ID {
    sprintf($$, "%s", $1);
}
        ;

%%

int yyerror()
{
    printf("Parsing is failed.\n");
    return 0;
}

int main(int argc, char *argv[])
{
    if(argc < 2)
    {
        printf("Please input the file name.\n");
        return 0;
    }
    if(argc > 4)
    {
        printf("Too many arguments.\n");
        return 0;
    }

    ir[0] = '\0';
    stack[0] = 1;
    ifstack[0] = 1;
    int outputSpecified = 0;

    FILE *input, *output;

    for(int i = 0; i < argc; i++)
    {
        if(strcmp(argv[i], "-o") == 0)
        {
            //output file name is the next thing
            i++;
            if(i >= argc)
            {
                printf("Please input the output file name.\n");
                return 0;
            }
            output = fopen(argv[i], "w");
            outputSpecified = 1;
            continue;
        }
        //input file name
        input = fopen(argv[i], "r");
    }
    //if no output file is specified, create one
    if(!outputSpecified)
    {
        output = fopen("output.ir", "w");
    }
    //parse input file
    yyin = input;
    yyparse();
    countline = 2;
    printf("1. ");
    for(int i = 0; i < strlen(ir); i++)
    {
        if(ir[i] == '\n')
        {
            printf("\n%d. ", countline);
            countline++;
        }
        else
            printf("%c", ir[i]);
    }
    printf("\n");

    //write ir into output file
    fwrite(ir, sizeof(char), strlen(ir), output);

    fclose(input);
    fclose(output);
    return 0;
}
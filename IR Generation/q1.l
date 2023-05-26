%{
    #include <stdio.h>
    #include "q1.tab.h"
    #include <string.h>
%}

%%
[ \t\n]+  {}
"while" return WHILE;
"do" return DO;
"print" return PRINT;
"or"    return OR;
"and"    return AND;
"if"     return IF;
"else"   return ELSE;
[0-9]+    {
    strcpy(yylval.str, yytext);
    return NUM;
}
[A-Za-z]([A-Za-z]|[0-9])*    {
    strcpy(yylval.str, yytext);
    return ID;
}
"(" return OP;
")" return CP;
"<="    return LE;
">="    return GE;
"=="    return EQ;
"!="    return NE;
"$" return END;
. {return yytext[0];}
%%

int yywrap()
{
    return 0;
}
# take filename as command line arg

if [ $# -ne 3 ]
then
    echo "Usage: $0 filename ir_filename num_of_registers"
    exit 1
fi

if [ ! -f $1 ]
then
    echo "File $1 not found!"
    exit 2
fi

#generate IR
./IR\ Generation/IR $1 -o $2

#run liveness script on ir
python3 Chaitin-Briggs/liveness.py $2 $3
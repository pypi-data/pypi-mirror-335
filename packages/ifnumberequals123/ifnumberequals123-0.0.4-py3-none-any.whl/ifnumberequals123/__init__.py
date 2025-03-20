def CreateCode(amount: int, numberVariableName: str = "number", fileName: str = "mycode") -> str:
    """
    Creates the code and writes it to a file.

    Parameters:
    amount (int): Amount of if number == amount.
    numberVariableName (str): The name of the variable that the number will have.
    fileName (str): the name of the file (.py is added automatically).
    
    Returns:
    str: The code.
    """
    finalCode = numberVariableName + " = int(input('input your number'))\n"
    for i in range(0, amount + 1):
        if i != amount:
            finalCode += f"if {numberVariableName} == {i}:\n\tprint('Your number is {i}')\n"
        else:
            finalCode += f"if {numberVariableName} == {i}:\n\tprint('Your number is {i}')"
    with open(fileName + ".py", "w") as file:
        file.write(finalCode)
    return finalCode
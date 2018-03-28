# Main class for an AT parser

USE_RE = False


class ParserAT:
    """
    
    """

    def __init__(self):
        self._cmd_list = {}
        self._operands = "=?"
        self._error_response = "ERROR"
        self._ok_response = "OK"

    def parse(self, input_str):
        """Parsing function taking one command string and returning tuple of response strings or None if parsing went wrong"""
        # RE version 
        if USE_RE:
            import re
            gen_syntax = re.compile(r"AT(?:\+(?P<OPCODE>[A-Z]+)(?:(?P<OPERAND>[=\?])(?P<PARAMS>[a-zA-Z0-9,._-]*))?)?")

            gen_syntax_match = gen_syntax.fullmatch(input_str)
            if gen_syntax_match:
                print("Matches: ", gen_syntax_match.groups())
                opcode = gen_syntax_match.group('OPCODE')
                operand = gen_syntax_match.group('OPERAND')
                params = gen_syntax_match.group('PARAMS')
                if opcode:
                    if opcode in self._cmd_list:
                        response = self._cmd_list[opcode](operand, params)
                        if response:
                            return response, self._ok_response
                        else:
                            return self._ok_response
                    else:
                        print("Command not found!")
                        return self._error_response
                else:
                    return "OK"  # Normal response to AT cmd
            else:
                print("Cannot parse input!")
                return "ERROR"

        # Simple string splitting version
        else:
            if input_str.startswith("AT"):
                if input_str.startswith("+", 2):
                    opcode = input_str[3:]  # In case there is no operand
                    operand = ""
                    params = ""
                    for op in self._operands:
                        if op in input_str:
                            split_list = input_str[3:].split(op, 1)
                            if len(split_list) > 1:
                                opcode = split_list[0]
                                operand = op
                                params = split_list[1]
                                break

                    if opcode in self._cmd_list:
                        response = self._cmd_list[opcode](operand, params)
                        if response:
                            return response, self._ok_response
                        else:
                            return self._ok_response
                    else:
                        print("Command unknown!")
                        return self._error_response

                elif input_str == "AT":
                    return "OK"

            print("Not valid AT command!")
            return self._error_response

    def add_command(self, opcode, command):
        self._cmd_list[opcode] = command

    def remove_command(self, opcode):
        if opcode in self._cmd_list:
            del self._cmd_list[opcode]

    def set_operands(self, operands):
        self._operands = operands

    def set_ok_response(self, ok_response):
        self._ok_response = ok_response

    def set_error_response(self, error_response):
        self._error_response = error_response

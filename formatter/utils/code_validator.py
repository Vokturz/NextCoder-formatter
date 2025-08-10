from tree_sitter_languages import get_parser

class CodeValidator:
    def __init__(self, language):
        self.language = language
        self.parser = get_parser(language)

        
    def validate_syntax(self, code_string: str) -> bool:
        tree = self.parser.parse(bytes(code_string, "utf8"))
        if tree.root_node.has_error:
            return False
        
        if tree.root_node.type == 'ERROR' and tree.root_node.has_error:
            return False

        return True

validators = {
    'python': CodeValidator('python'),
    'javascript': CodeValidator('javascript'),
    'java': CodeValidator('java'),
    'cpp': CodeValidator('cpp'),
    'c': CodeValidator('cpp'),
    'go': CodeValidator('go'),
    'kotlin': CodeValidator('kotlin'),
    'rust': CodeValidator('rust'),
}

def validate_code(language, code_string):
    try:
        if language == '':
            return {
                "valid": False
            }

        if language not in validators:
            print(f"Unsupported language: {language}")
            return {
                "valid": False
            }
        return {
            "valid": validators[language].validate_syntax(code_string)
        }
    except Exception as e:
        print(e)
        return { "valid": False }
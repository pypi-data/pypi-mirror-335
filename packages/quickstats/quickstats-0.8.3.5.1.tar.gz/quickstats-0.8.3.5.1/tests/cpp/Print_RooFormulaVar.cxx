#include <RooRealVar.h>
#include <RooFormulaVar.h>
#include <RooArgSet.h>
#include <iostream>
#include <string>

std::string formatFunctionStr(const std::string class_name, const std::string name, 
                              const std::string formula_str){
    std::string ret = class_name + "::" + name + "[ " + formula_str + " ]";
    return ret;
}
std::string getFunctionStrRepr(RooFormulaVar &formula_var){
    // 
    std::string formula_str = formula_var.expression();
    const RooArgSet dependents = formula_var.dependents();
    for (unsigned int i = 0; i < dependents.size(); ++i) {
        const auto& var = dependents[i];
        std::stringstream regexStr;
        regexStr << "x\\[" << i << "\\]|@" << i;
        std::regex regex(regexStr.str());
        std::string replacement = var->GetName();
        formula_str = std::regex_replace(formula_str, regex, replacement);
    }
    std::string ret = formatFunctionStr(formula_var.ClassName(), formula_var.GetName(), formula_str );
    return ret;
}

int Print_RooFormulaVar() {
    RooRealVar x("x", "Variable x", 1.0);
    RooRealVar y("y", "Variable y", 2.0);

    std::string formulaStr = "@0+@1";

    RooFormulaVar formulaVar("formulaVar", "Test Formula", formulaStr.c_str(), RooArgSet(x, y));

    std::string result = getFunctionStrRepr(formulaVar);
    std::cout << "Reconstructed Formula String: " << result << std::endl;

    formulaStr = "x[0]+x[1]";

    RooFormulaVar formulaVar1("formulaVar", "Test Formula", formulaStr.c_str(), RooArgSet(x, y));

    result = getFunctionStrRepr(formulaVar1);
    std::cout << "Reconstructed Formula String: " << result << std::endl;

    formulaStr = "x+y";

    RooFormulaVar formulaVar2("formulaVar", "Test Formula", formulaStr.c_str(), RooArgSet(x, y));

    result = getFunctionStrRepr(formulaVar2);
    std::cout << "Reconstructed Formula String: " << result << std::endl;

    return 0;
}
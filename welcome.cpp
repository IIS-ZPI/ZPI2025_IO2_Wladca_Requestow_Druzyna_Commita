#include <iostream>

#include "ArithmeticsAdd.hpp"
#include "ArithmeticsDiff.hpp"

int main() {
    std::string msg =   "Group name : Wladca_Requestow_Druzyna_Commita\n"
                        "SCRUM Master : Tymoteusz Kot\n"
                        "Github : 252803@edu.p.lodz.pl\n"
                        "Tester : Tobiasz Grala\n"
                        "Github : Pjongi\n";

    std::cout << msg << std::endl;

    /* ADDITION */
    IArithmeticsAdd *mathAdd = new ArithmeticsAdd();
    double add_res = mathAdd->Addition(5, 10);
    std::cout << "Addition result of [5 + 10] = " << add_res << std::endl;

    /* SUBTRACTION */
    IArithmeticsDiff *mathDiff = new ArithmeticsDiff();
    double diff_res = mathDiff->Difference(10, 4);
    std::cout << "Subtraction result of [10 - 4] = " << diff_res << std::endl;

    return 0;
}
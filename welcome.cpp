#include <iostream>

#include "Addition.hpp"
#include "ArithmeticsDiff.hpp"

int main() {
    std::string msg =   "Group name : Wladca_Requestow_Druzyna_Commita\n"
                        "SCRUM Master : Tymoteusz Kot\n"
                        "Github : 252803@edu.p.lodz.pl\n"
                        "Tester : Tobiasz Grala\n"
                        "Github : Pjongi";

    std::cout << msg << std::endl;

    /* ADDITION */
    IArithmeticsAdd *add = new Add();
    double add_res = add->Addition(5,10);
    std::cout << "Addition result : " << add_res << std::endl;

    /* Odejmowanie */
    ArithmeticsDiff mathDiff;
    std::cout << "Wynik odejmowania 10 - 4 = " << mathDiff.Difference(10, 4) << std::endl;
    return 0;
}
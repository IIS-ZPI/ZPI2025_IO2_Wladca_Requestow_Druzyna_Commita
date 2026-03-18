#include <iostream>

#include "ArithmeticsAdd.hpp"
#include "ArithmeticsDiff.hpp"
#include "ArithmeticsMult.hpp"
#include "ArithmeticsDiv.hpp"

int main() {
    std::string msg =   "Group name : Wladca_Requestow_Druzyna_Commita\n"
                        "SCRUM Master : Tymoteusz Kot\n"
                        "Github : 252803@edu.p.lodz.pl\n"
                        "Tester : Tobiasz Grala\n"
                        "Github : Pjongi\n"
                        "Developer : Szymon Pokora\n"
                        "Github : SzymonPokora\n"
                        "DevOps : Urszula Szmit\n"
                        "Github : Urszula8\n";

    std::cout << msg << std::endl;

    /* ADDITION */
    IArithmeticsAdd *mathAdd = new ArithmeticsAdd();
    double add_res = mathAdd->Addition(5, 10);
    std::cout << "Addition result of [5 + 10] = " << add_res << std::endl;

    /* SUBTRACTION */
    IArithmeticsDiff *mathDiff = new ArithmeticsDiff();
    double diff_res = mathDiff->Difference(10, 4); // 6 7
    std::cout << "Subtraction result of [10 - 4] = " << diff_res << std::endl;

    /* MULTIPLICATION */
    IArithmeticsMult *mathMult = new ArithmeticsMult();
    double mult_res = mathMult->Multiplication(5, 3); //6 7
    std::cout << "Multiplication result of [5 * 3] = " << mult_res << std::endl;

    //DIVISION
    IArithmeticsDiv *mathDiv = new ArithmeticsDiv();
    double div_res = mathDiv->Division(12, 2); //6 7
    std::cout << "Division result of [12 / 2] = " << div_res << std::endl;


    return 0;
}

#include <iostream>

#include "Addition.hpp"

int main() {
    std::string msg =   "Group name : Wladca_Requestow_Druzyna_Commita\n"
                        "SCRUM Master : Tymoteusz Kot\n"
                        "Github : 252803@edu.p.lodz.pl";

    std::cout << msg << std::endl;

    /* ADDITION */
    IArithmeticsAdd *add = new Add();
    double add_res = add->Addition(5,10);
    std::cout << "Addition result : " << add_res << std::endl;

    return 0;
}
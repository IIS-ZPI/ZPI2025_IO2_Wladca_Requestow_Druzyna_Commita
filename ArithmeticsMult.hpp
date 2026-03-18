#pragma once

class IArithmeticsMult {
public:
    virtual double Multiplication(double A, double B) = 0;
};

class ArithmeticsMult : public IArithmeticsMult {
public:
    double Multiplication(double A, double B) override;
};

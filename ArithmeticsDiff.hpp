#pragma once

class IArithmeticsDiff {
public:
    virtual double Difference(double A, double B) = 0;
    virtual ~IArithmeticsDiff() = default;
};

class ArithmeticsDiff : public IArithmeticsDiff {
public:
    double Difference(double A, double B) override;
};
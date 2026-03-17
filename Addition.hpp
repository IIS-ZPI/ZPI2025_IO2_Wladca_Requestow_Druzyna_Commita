#pragma once

class IArithmeticsAdd
{
public:
    virtual double Addition(double A, double B) = 0;
    virtual ~IArithmeticsAdd() {};
};

class Add : public IArithmeticsAdd
{
    double Addition(double A, double B) override;
};
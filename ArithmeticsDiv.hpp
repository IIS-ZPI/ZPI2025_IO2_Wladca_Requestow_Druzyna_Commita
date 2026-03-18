#pragma once

class IArithmeticsDiv {
public:
    virtual double Division(double A, double B) = 0;
    virtual ~IArithmeticsDiv() = default;
};

class ArithmeticsDiv : public IArithmeticsDiv {
public:
    double Division(double A, double B) override;
};

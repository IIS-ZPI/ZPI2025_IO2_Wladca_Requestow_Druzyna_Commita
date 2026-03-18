// To jest komentarz, który za chwilę usunę przez revert

#pragma once

class IArithmeticsAdd {
public:
    virtual double Addition(double A, double B) = 0;
    virtual ~IArithmeticsAdd() = default;
};

class ArithmeticsAdd : public IArithmeticsAdd {
public:
    double Addition(double A, double B) override;
};
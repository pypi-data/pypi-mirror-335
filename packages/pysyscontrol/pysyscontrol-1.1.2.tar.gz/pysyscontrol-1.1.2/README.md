# PyControl
A series of python classes to quickly analyse control systems down from the governing differential equation.
The classes allow for the equations to be entered easily and intuitively. 

Guidelines for entering a differential equation:
  Use double quotes, Lagrange notation uses single quotes for derivatives
  For multiplication use an asterisk
  For subtraction use +-, as in 5+-3. (There is a mathematical reason why this is more correct than 5-3, but that's beside the point)
The above guidelines are also listed in the documentation.

The laplace_handler transforms the given equation from whatever domain it is defined on, which it is assumed to be the time-domain,
to the complex valued s-domain.

The transfer_function class converts the given differential equations to a transfer function in the s-domain, which can be switched to the w-domain.

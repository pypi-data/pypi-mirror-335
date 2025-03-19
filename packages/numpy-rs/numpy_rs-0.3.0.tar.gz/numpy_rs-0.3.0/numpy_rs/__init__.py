from .exp import Experiments

# Create an instance of Experiments
_exp_runner = Experiments()

# Expose exp() directly at the module level
exp = _exp_runner.exp  # Now numpy_rs.exp() will work
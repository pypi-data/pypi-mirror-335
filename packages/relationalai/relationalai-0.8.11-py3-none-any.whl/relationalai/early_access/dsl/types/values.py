import relationalai.early_access.dsl.core.types.constrained.nominal
import relationalai.early_access.dsl.core.types.constrained.subtype
from relationalai.early_access.dsl.types import Type


class ValueType(Type, relationalai.early_access.dsl.core.types.constrained.nominal.ValueType):

    def __init__(self, model, nm, *args):
        super().__init__(model, nm)
        relationalai.early_access.dsl.core.types.constrained.nominal.ValueType.__init__(self, nm, *args)


class ValueSubtype(Type, relationalai.early_access.dsl.core.types.constrained.subtype.ValueSubtype):

    def __init__(self, model, nm, *args):
        super().__init__(model, nm)
        relationalai.early_access.dsl.core.types.constrained.subtype.ValueSubtype.__init__(self, nm, *args)

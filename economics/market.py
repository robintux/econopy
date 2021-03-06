#!/usr/bin/env python

import sympy as sp
from consumer import Consumer, ConsumerAggregate
from producer import Firm, ProducerAggregate
import economics.tools as et

class Market(object):
    def __init__(self, q, p, demand, supply, deluded_demand=None):
        self.demand = demand
        self.deluded_demand = deluded_demand
        self.supply = supply
        self.p = p
        self.q = q

    def equilibrium(self, rational=True):
        """
        >>> sp.var('x p', positive=True)
        (x, p)
        >>> consumer = Consumer(x, p, 20*sp.sqrt(x), W=100)
        >>> cons_aggregate = ConsumerAggregate((consumer, 100))
        >>> cons_aggregate.demand()
        Piecewise((0, p < 0), (10000/p**2, 0 < p), (0, True))
        >>> firm = Firm(x, p, 1/2. * x**2, SFC=0, FC=0)
        >>> firm_aggregate = ProducerAggregate((firm, 10))
        >>> firm_aggregate.supply()
        Piecewise((0, p < 0), (10*p, And(0 <= p, p >= 0)))
        >>> mkt = Market(x, p,
        ...              cons_aggregate.demand(),
        ...              firm_aggregate.supply())
        >>> mkt.equilibrium()
        (10, 100)
        >>> mkt = Market(x, p,
        ...              demand=1000-p,
        ...              supply=sp.Eq(p, 100))
        >>> mkt.equilibrium()
        (100, 900)
        """
        demand = self.demand
        if not rational:
            demand = self.deluded_demand
        eq = sp.solve((et.implicit(self.q, demand),
                       et.implicit(self.q, self.supply)),
                      self.p, self.q, dict=True)
        if eq:
            eq = eq[-1]
            return eq[self.p], eq[self.q] #self.supply.subs(self.p, peq)

        peq = sp.solve(sp.piecewise_fold(demand - self.supply), self.p)
        if peq:
            peq = peq[-1]
            return peq, self.supply.subs(self.p, peq)
        return None, None

    def total_cost(self):
        return et.cost_from_supply(self.q, self.p, self.supply)

    def total_benefit(self):
        return et.benefit_from_demand(self.q, self.p, self.demand)

    def total_cost_at_p(self):
        return self.total_cost().subs(self.q, self.demand)

    def total_benefit_at_p(self, rational=True):
        demand = self.demand
        if not rational:
            demand = self.deluded_demand
        return self.total_benefit().subs(self.q, demand)

    def social_surplus(self):
        return self.total_benefit() - self.total_cost()

    def social_surplus_at_p(self):
        return (self.total_benefit_at_p() -
                self.total_cost_at_p())

    def consumer_surplus(self):
        peq, qeq = self.equilibrium()
        if peq is None:
            return 0
        benefit = self.total_benefit()
        return benefit.subs(self.q, qeq) - peq*qeq

    def producer_surplus(self):
        peq, qeq = self.equilibrium()
        if peq is None:
            return 0
        return peq*qeq - self.total_cost().subs(self.q, qeq)

    def free_market_social_surplus(self):
        """
        >>> sp.var('x p', positive=True)
        (x, p)
        >>> consumer = Consumer(x, p, 20*sp.sqrt(x), W=100)
        >>> cons_aggregate = ConsumerAggregate((consumer, 100))
        >>> firm = Firm(x, p, 1/2. * x**2, SFC=0, FC=0)
        >>> firm_aggregate = ProducerAggregate((firm, 10))
        >>> mkt = Market(x, p,
        ...              cons_aggregate.demand(),
        ...              firm_aggregate.supply())
        >>> peq, qeq = mkt.equilibrium()
        >>> (mkt.social_surplus().subs(x, qeq) ==
        ...     mkt.free_market_social_surplus())
        True
        """
        peq = self.equilibrium()[0]
        if peq is None:
            return 0
        return self.consumer_surplus() + self.producer_surplus()


def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()

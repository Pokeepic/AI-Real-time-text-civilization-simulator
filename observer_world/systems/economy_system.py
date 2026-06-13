"""
Economy system for Observer World.
"""

import random


def handle_trade(sim, agent):
    logs = []

    nearby = [
        other for other in sim.nearby_agents(agent)
        if other.alive and other.name != agent.name
    ]

    if not nearby:
        logs.append(f"{agent.name} wanted to trade, but no one was nearby.")
        return logs

    other = random.choice(nearby)

    trade_gain = random.randint(1, 4)

    agent.wealth += trade_gain
    other.wealth += 1

    agent.improve_skill("social", 1)
    other.improve_skill("social", 1)

    agent.change_relationship(other.name, "trust", 2)
    other.change_relationship(agent.name, "trust", 2)

    logs.append(f"{agent.name} traded with {other.name}.")
    logs.append(f"{agent.name} wealth +{trade_gain}. {other.name} wealth +1.")

    return logs

def handle_gamble(sim, agent):
    logs = []

    if agent.wealth <= 0:
        logs.append(f"{agent.name} wanted to gamble, but had no wealth.")
        return logs

    bet = random.randint(1, min(agent.wealth, 3))

    if random.random() < 0.45:
        winnings = bet * 2
        agent.wealth += winnings
        logs.append(f"{agent.name} gambled and won {winnings} wealth.")
    else:
        agent.wealth -= bet
        logs.append(f"{agent.name} gambled and lost {bet} wealth.")

    agent.improve_skill("social", 1)

    return logs

def handle_repay_debt(sim, agent):
    logs = []

    if not agent.debts:
        logs.append(f"{agent.name} had no debts to repay.")
        return logs

    creditor_name = random.choice(list(agent.debts.keys()))
    amount = agent.debts[creditor_name]

    if agent.wealth <= 0:
        logs.append(f"{agent.name} wanted to repay {creditor_name}, but had no wealth.")
        return logs

    payment = min(agent.wealth, amount)

    agent.wealth -= payment
    agent.debts[creditor_name] -= payment

    creditor = next((a for a in sim.agents if a.name == creditor_name), None)

    if creditor:
        creditor.wealth += payment
        creditor.change_relationship(agent.name, "trust", 3)
        agent.change_relationship(creditor.name, "trust", 2)

    logs.append(f"{agent.name} repaid {payment} wealth to {creditor_name}.")

    if agent.debts[creditor_name] <= 0:
        del agent.debts[creditor_name]
        logs.append(f"{agent.name} fully repaid their debt to {creditor_name}.")

    return logs

def handle_demand_debt(sim, agent):
    logs = []

    debtors = [
        other for other in sim.agents
        if agent.name in other.debts and other.alive
    ]

    if not debtors:
        logs.append(f"{agent.name} had no debts to demand.")
        return logs

    debtor = random.choice(debtors)
    amount = debtor.debts[agent.name]

    logs.append(f"{agent.name} demanded repayment from {debtor.name}.")

    if debtor.wealth > 0:
        payment = min(debtor.wealth, amount)

        debtor.wealth -= payment
        debtor.debts[agent.name] -= payment
        agent.wealth += payment

        debtor.change_relationship(agent.name, "fear", 2)
        agent.change_relationship(debtor.name, "trust", -1)

        logs.append(f"{debtor.name} paid {payment} wealth to {agent.name}.")

        if debtor.debts[agent.name] <= 0:
            del debtor.debts[agent.name]
            logs.append(f"{debtor.name} fully repaid their debt to {agent.name}.")
    else:
        debtor.change_relationship(agent.name, "fear", 5)
        debtor.change_relationship(agent.name, "trust", -3)

        logs.append(f"{debtor.name} could not repay the debt.")

    return logs
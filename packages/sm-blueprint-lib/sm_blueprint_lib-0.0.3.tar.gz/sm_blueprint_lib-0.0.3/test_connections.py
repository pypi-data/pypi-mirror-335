from pprint import pp

from numpy import ndarray

from sm_blueprint_lib import Timer, LogicGate, BarrierBlock, Blueprint, save_blueprint, dump_string, connect

size = 10
l0 = [
    LogicGate((x+1, 0, 0), "FF0000", x % 6)
    for x in range(size)
]

l1 = [
    LogicGate((0, x+1, 0), "00FF00", x % 6)
    for x in range(size)
]

l2 = [
    LogicGate((0, 0, x+1), "0000FF", x % 6)
    for x in range(size)
]

# l3 = [
#     [Timer((x+1, y+1, x+y), "000000", (2, 1)) for y in range(size)]
#     for x in range(size)
# ]
l3 = ndarray((size, size), dtype=Timer)
for x in range(size):
    for y in range(size):
        l3[x, y] = Timer((x+1, y+1, x+y), "000000", (2, 1))
base = BarrierBlock((0, -1, -1), "000000", (size+1, size+1, 1))
zero = BarrierBlock((0, -1, 0), "000000", (1, 1, 1))

bp = Blueprint()

connect(l0, l1)
connect(l0, l3)
connect(l3, l2[-1])
connect(l1, l2, parallel=False)
connect(l3.T, l1)

bp.add(l0, l1, l2, base, zero, l3)

# bp.add(l0)
# bp.add(l1)
# bp.add(l2)

# bp.add(base)
# bp.add(zero)
# bp.add(l3)


# bp.bodies[0].childs.extend(l0)
# bp.bodies[0].childs.extend(l1)
# bp.bodies[0].childs.extend(l2)

# bp.bodies[0].childs.append(base)
# bp.bodies[0].childs.append(zero)

# for l in l3:
#     bp.bodies[0].childs.extend(l)

print(len(bp.bodies[0].childs))
path = r"C:\Users\mauri\AppData\Roaming\Axolot Games\Scrap Mechanic\User\User_76561198400983548\Blueprints\c35f6e4e-52cb-4b00-8afa-f0ffd3fbb012\blueprint.json"
save_blueprint(path, bp)

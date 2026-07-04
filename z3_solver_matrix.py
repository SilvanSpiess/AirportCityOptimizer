import z3
import math

def count_propositions(solver, name, props):
   countProps = [z3.Int(f"{name}.count{i}") for i in range(len(props))]
   resultCount = z3.Int(f"{name}.counted")
   countProps.append(resultCount)
   solver.add(countProps[0] == 0)
   for i in range(len(props)):
      solver.add(z3.Implies(props[i], countProps[i+1] == countProps[i] + 1))
      solver.add(z3.Implies(z3.Not(props[i]), countProps[i+1] == countProps[i]))
   return resultCount

def z3_min(lst):
   m = lst[0]
   for x in lst[1:]:
      m = z3.If(x < m, x, m)
   return m

def final_passenger_yields(passenger, num_trees):
   boosted = passenger * (1 + 0.1 * num_trees)
   return math.ceil(boosted) 

def to_python(val):
   # Check if it's a Boolean result
   if hasattr(val, 'is_true'):
      return 1 if val.is_true() else 0
   # Check if it's an Integer result
   if hasattr(val, 'as_long'):
      return val.as_long()
   # Fallback for Reals or other types
   return str(val)

#   0 = empty
#   1 = visa
#   2 = road
#   3 = tree
#   4 -  8 small houses
#   9 - 29 top left big houses (main)
#  30 - 48 top right big houses (administration)
#  49 - 68 bottom left big houses (administration)
#  69 - 88 bottom right big houses (administration)
#  89 - 91 top left huge houses (main)
#  92 - 94 top right huge houses (administration)
#  95 - 97 bottom left huge houses (administration)
#  98 - 100 bottom right huge houses (administration)

#  ----
#  |TL|
#  ----

#  -------
#  |TL|TR|
#  -------
#  |BL|BR|
#  -------

#  -----------
#  |TL|  TR  |
#  -----------
#  |  |      |
#  -BL-  BR  -
#  |  |      |
#  -----------

id_to_name = {0: "empty", 1: "visa", 2: "road", 3: "tree"}

def run_z3_solver(HOUSE: dict):
   field_width = 9
   field_height = 9
   visa_locs = [(4, 4)]
   visa_range = 2

   meta_keys = ["empty", "visa", "road", "tree"]
   META_ID = {name: i for i, name in enumerate(meta_keys)}

   houses_by_size = {
      "small": [n for n, d in HOUSE.items() if d["size"] == 1 and n not in meta_keys],
      "big":   [n for n, d in HOUSE.items() if d["size"] == 2 and n not in meta_keys],
      "huge":  [n for n, d in HOUSE.items() if d["size"] == 3 and n not in meta_keys]
   }
   nr_small_houses = len(houses_by_size["small"])
   nr_big_houses = len(houses_by_size["big"])
   nr_huge_houses = len(houses_by_size["huge"])

   begin_small_houses =    4
   end_small_houses =      begin_small_houses + nr_small_houses

   big_house_TL_begin = end_small_houses
   big_house_TL_end   = big_house_TL_begin + nr_big_houses
   big_house_TR_begin = big_house_TL_end
   big_house_TR_end   = big_house_TR_begin + nr_big_houses
   big_house_BL_begin = big_house_TR_end
   big_house_BL_end   = big_house_BL_begin + nr_big_houses
   big_house_BR_begin = big_house_BL_end
   big_house_BR_end   = big_house_BR_begin + nr_big_houses

   huge_house_TL_begin = big_house_BR_end
   huge_house_TL_end   = huge_house_TL_begin + nr_huge_houses
   huge_house_TR_begin = huge_house_TL_end
   huge_house_TR_end   = huge_house_TR_begin + nr_huge_houses
   huge_house_BL_begin = huge_house_TR_end
   huge_house_BL_end   = huge_house_BL_begin + nr_huge_houses
   huge_house_BR_begin = huge_house_BL_end
   huge_house_BR_end   = huge_house_BR_begin + nr_huge_houses

   #s = z3.Solver()
   s = z3.Optimize()

   field = [[{
      "kind": z3.Int(f"field_kind_at_{x},{y}"),
      "small_tree": z3.Int(f"trees_nearby_small_at_{x},{y}"),
      "big_tree": z3.Int(f"trees_nearby_big_at_{x},{y}"),
      "huge_tree": z3.Int(f"trees_nearby_huge_at_{x},{y}"),
      "has_visa": z3.Bool(f"has_visa_{x},{y}"),
      "value": z3.Int(f"value_at_{x},{y}")
   } for x in range(field_width)] for y in range(field_height)]

   #only existing structures
   for y in range(field_height):
      for x in range(field_width):
         if (x, y) in visa_locs:
            s.add(field[y][x]["kind"] == META_ID["visa"])
         else:
            s.add(field[y][x]["kind"] != META_ID["visa"])
            s.add(field[y][x]["kind"] >= 0)
            s.add(field[y][x]["kind"] < huge_house_BR_end)

   # make sure big houses are whole
   for y in range(field_height):
      for x in range(field_width):
         # if is topleft of house, then make sure the other corners are there
         s.add(
            z3.Implies(
               z3.And(
                  field[y][x]["kind"] >= big_house_TL_begin, field[y][x]["kind"] < big_house_TL_end),
               z3.And(
                  field[y][x+1]["kind"] - big_house_TR_begin == field[y][x]["kind"]-big_house_TL_begin if x+1 < field_width else False,
                  field[y+1][x]["kind"] - big_house_BL_begin == field[y][x]["kind"]-big_house_TL_begin if y+1 < field_height else False,
                  field[y+1][x+1]["kind"]-big_house_BR_begin == field[y][x]["kind"]-big_house_TL_begin if x+1 < field_width and y+1 < field_height else False
               )
            )
         )
         # if is topright of house, then check if topleft is there
         s.add(z3.Implies(
            z3.And(
               field[y][x]["kind"] >= big_house_TR_begin, field[y][x]["kind"] < big_house_TR_end),
            field[y][x-1]["kind"] - big_house_TL_begin == field[y][x]["kind"] - big_house_TR_begin if x-1 >= 0 else False
         ))
         # if is bottomleft of house, then check if topleft is there
         s.add(z3.Implies(
            z3.And(
               field[y][x]["kind"] >= big_house_BL_begin, field[y][x]["kind"] < big_house_BL_end),
            field[y-1][x]["kind"] - big_house_TL_begin == field[y][x]["kind"] - big_house_BL_begin if y-1 >= 0 else False
         ))
         # if is bottomright of house, then check if topleft is there
         s.add(z3.Implies(
            z3.And(
               field[y][x]["kind"] >= big_house_BR_begin, field[y][x]["kind"] < big_house_BR_end),
            field[y-1][x-1]["kind"] - big_house_TL_begin == field[y][x]["kind"] - big_house_BR_begin if x-1 >= 0 and y-1 >= 0 else False
         ))

   # make sure huge houses are whole
   for y in range(field_height):
      for x in range(field_width):
         # if is topleft of house, then make sure the other corners are there
         s.add(
            z3.Implies(
               z3.And(
                  field[y][x]["kind"] >= huge_house_TL_begin, field[y][x]["kind"] < huge_house_TL_end),
               z3.And(
                  field[y][x+1]["kind"] - huge_house_TR_begin == field[y][x]["kind"]-huge_house_TL_begin if x+1 < field_width else False,
                  field[y][x+2]["kind"] - huge_house_TR_begin == field[y][x]["kind"]-huge_house_TL_begin if x+2 < field_width else False,
                  field[y+1][x]["kind"] - huge_house_BL_begin == field[y][x]["kind"]-huge_house_TL_begin if y+1 < field_height else False,
                  field[y+2][x]["kind"] - huge_house_BL_begin == field[y][x]["kind"]-huge_house_TL_begin if y+2 < field_height else False,
                  field[y+1][x+1]["kind"]-huge_house_BR_begin == field[y][x]["kind"]-huge_house_TL_begin if x+1 < field_width and y+1 < field_height else False,
                  field[y+1][x+2]["kind"]-huge_house_BR_begin == field[y][x]["kind"]-huge_house_TL_begin if x+2 < field_width and y+1 < field_height else False,
                  field[y+2][x+1]["kind"]-huge_house_BR_begin == field[y][x]["kind"]-huge_house_TL_begin if x+1 < field_width and y+2 < field_height else False,
                  field[y+2][x+2]["kind"]-huge_house_BR_begin == field[y][x]["kind"]-huge_house_TL_begin if x+2 < field_width and y+2 < field_height else False
               )
            )
         )
         # if is topright of house, then check if topleft is there
         s.add(z3.Implies(
            z3.And(
               field[y][x]["kind"] >= huge_house_TR_begin,
               field[y][x]["kind"] < huge_house_TR_end
            ),
            z3.Or(
               field[y][x-1]["kind"] - huge_house_TL_begin == field[y][x]["kind"] - huge_house_TR_begin if x-1 >= 0 else False,
               field[y][x-2]["kind"] - huge_house_TL_begin == field[y][x]["kind"] - huge_house_TR_begin if x-2 >= 0 else False
            )
         ))
         # if is bottomleft of house, then check if topleft is there
         s.add(z3.Implies(
            z3.And(
               field[y][x]["kind"] >= huge_house_BL_begin,
               field[y][x]["kind"] < huge_house_BL_end
            ),
            z3.Or(
               field[y-1][x]["kind"] - huge_house_TL_begin == field[y][x]["kind"] - huge_house_BL_begin if y-1 >= 0 else False,
               field[y-2][x]["kind"] - huge_house_TL_begin == field[y][x]["kind"] - huge_house_BL_begin if y-2 >= 0 else False
            )
         ))
         # if is bottomright of house, then check if topleft is there
         s.add(z3.Implies(
            z3.And(
               field[y][x]["kind"] >= huge_house_BR_begin,
               field[y][x]["kind"] < huge_house_BR_end
            ),
            z3.Or(
               field[y-1][x-1]["kind"] - huge_house_TL_begin == field[y][x]["kind"] - huge_house_BR_begin if x-1 >= 0 and y-1 >= 0 else False,
               field[y-1][x-2]["kind"] - huge_house_TL_begin == field[y][x]["kind"] - huge_house_BR_begin if x-2 >= 0 and y-1 >= 0 else False,
               field[y-2][x-1]["kind"] - huge_house_TL_begin == field[y][x]["kind"] - huge_house_BR_begin if x-1 >= 0 and y-2 >= 0 else False,
               field[y-2][x-2]["kind"] - huge_house_TL_begin == field[y][x]["kind"] - huge_house_BR_begin if x-2 >= 0 and y-2 >= 0 else False
            )
         ))

   # make sure visas and small houses have roads
   for y in range(field_height):
      for x in range(field_width):
         s.add(
            z3.Implies(
               z3.Or(
                  field[y][x]["kind"] == META_ID["visa"], # is visa
                  z3.And(
                     field[y][x]["kind"] >= begin_small_houses,
                     field[y][x]["kind"] <  end_small_houses # or is small house
                  )
               ),
               z3.Or( # above, below, left or right is road
                  field[y-1][x]["kind"] == META_ID["road"] if y-1 >= 0 else False,
                  field[y+1][x]["kind"] == META_ID["road"] if y+1 < field_height else False,
                  field[y][x-1]["kind"] == META_ID["road"] if x-1 >= 0 else False,
                  field[y][x+1]["kind"] == META_ID["road"] if x+1 < field_width else False,
               )
            )
         )
         # make sure big houses have roads
         s.add(
            z3.Implies(
               z3.Or(
                  field[y][x]["kind"] == META_ID["visa"], # is visa
                  z3.And(
                     field[y][x]["kind"] >= big_house_TL_begin,
                     field[y][x]["kind"] < big_house_TL_end # or is big house
                  )
               ),
               z3.Or( # above, below, left or right is road
                  #above
                  field[y-1][x]["kind"]   == META_ID["road"] if y-1 >= 0 else False,
                  field[y-1][x+1]["kind"] == META_ID["road"] if y-1 >= 0 and x+1 < field_width else False,
                  #below
                  field[y+2][x]["kind"]   == META_ID["road"] if y+2 < field_height else False,
                  field[y+2][x+1]["kind"] == META_ID["road"] if y+2 < field_height and x+1 < field_width else False,
                  #left
                  field[y][x-1]["kind"]   == META_ID["road"] if x-1 >= 0 else False,
                  field[y+1][x-1]["kind"] == META_ID["road"] if y+1 < field_height and x-1 >= 0 else False,
                  #right
                  field[y][x+2]["kind"]   == META_ID["road"] if x+2 < field_width else False,
                  field[y+1][x+2]["kind"] == META_ID["road"]if y+1 < field_height and x+2 < field_width else False,
               )
            )
         )
         # make sure huge houses have roads
         s.add(
            z3.Implies(
               z3.Or(
                  field[y][x]["kind"] == META_ID["visa"], # is visa
                  z3.And(
                     field[y][x]["kind"] >= huge_house_TL_begin,
                     field[y][x]["kind"] < huge_house_TL_end # or is huge house
                  )
               ),
               z3.Or( # above, below, left or right is road
                  #above
                  field[y-1][x]["kind"]   == META_ID["road"] if y-1 >= 0 else False,
                  field[y-1][x+1]["kind"] == META_ID["road"] if y-1 >= 0 and x+1 < field_width else False,
                  field[y-1][x+2]["kind"] == META_ID["road"] if y-1 >= 0 and x+2 < field_width else False,
                  #below
                  field[y+3][x]["kind"]   == META_ID["road"] if y+3 < field_height else False,
                  field[y+3][x+1]["kind"] == META_ID["road"] if y+3 < field_height and x+1 < field_width else False,
                  field[y+3][x+2]["kind"] == META_ID["road"] if y+3 < field_height and x+2 < field_width else False,
                  #left
                  field[y][x-1]["kind"]   == META_ID["road"] if x-1 >= 0 else False,
                  field[y+1][x-1]["kind"] == META_ID["road"] if y+1 < field_height and x-1 >= 0 else False,
                  field[y+2][x-1]["kind"] == META_ID["road"] if y+2 < field_height and x-1 >= 0 else False,
                  #right
                  field[y][x+3]["kind"]   == META_ID["road"] if x+3 < field_width else False,
                  field[y+1][x+3]["kind"] == META_ID["road"] if y+1 < field_height and x+3 < field_width else False,
                  field[y+2][x+3]["kind"] == META_ID["road"] if y+2 < field_height and x+3 < field_width else False
               )
            )
         )

   #which squares have visa
   for y in range(field_height):
      for x in range(field_width):
         square_range = [(x2, y2) 
                         for x2 in range(x-visa_range, x+visa_range+1) for y2 in range(y-visa_range, y+visa_range+1)
                         if x2>= 0 and x2 < field_width and y2>= 0 and y2 < field_height and not(x2 == x and y2 == y)]
         s.add(
            field[y][x]["has_visa"] == z3.Or([field[y2][x2]["kind"] == META_ID["visa"] for x2, y2 in square_range])
         )
         
   #houses near visa map
   for y in range(field_height):
      for x in range(field_width):
         s.add(z3.Implies( # is small house
            z3.And(
               field[y][x]["kind"] >= begin_small_houses,
               field[y][x]["kind"] < end_small_houses
            ), #distance to visa is max 1
            field[y][x]["has_visa"]
         ))
         s.add(z3.Implies( # is big house
            z3.And(
               field[y][x]["kind"] >= big_house_TL_begin,
               field[y][x]["kind"] < big_house_TL_end
            ), #distance to visa is max 1
            z3.Or(
               field[y][x]["has_visa"],
               field[y][x+1]["has_visa"] if x+1 < field_width else False,
               field[y+1][x]["has_visa"] if y+1 < field_height else False,
               field[y+1][x+1]["has_visa"] if y+1 < field_height and x+1 < field_width else False
            )
         ))
         s.add(z3.Implies( # is huge house
            z3.And(
               field[y][x]["kind"] >= huge_house_TL_begin,
               field[y][x]["kind"] < huge_house_TL_end
            ), #distance to visa is max 1
            z3.Or(
               field[y][x]["has_visa"],
               field[y][x+1]["has_visa"] if x+1 < field_width else False,
               field[y][x+2]["has_visa"] if x+2 < field_width else False,
               field[y+1][x]["has_visa"] if y+1 < field_height else False,
               field[y+2][x]["has_visa"] if y+2 < field_height else False,
               field[y+1][x+1]["has_visa"] if y+1 < field_height and x+1 < field_width else False,
               field[y+1][x+2]["has_visa"] if y+1 < field_height and x+2 < field_width else False,
               field[y+2][x+1]["has_visa"] if y+2 < field_height and x+1 < field_width else False,
               field[y+2][x+2]["has_visa"] if y+2 < field_height and x+2 < field_width else False
            )
         ))

   #tree counting
   for y in range(field_height):
      for x in range(field_width):
         squares_in_range_small = [(x2, y2) 
                                   for x2 in range(x-1, x+2) for y2 in range(y-1, y+2)
                                   if x2>= 0 and x2 < field_width and y2>= 0 and y2 < field_height and not(x2 == x and y2 == y)]
         squares_in_range_big = [(x2, y2) 
                                 for x2 in range(x-1, x+3) for y2 in range(y-1, y+3)
                                 if x2>= 0 and x2 < field_width and y2>= 0 and y2 < field_height and \
                                 not((x2 == x or x2 == x+1) and (y2 == y or y2 == y+1))]
         
         squares_in_range_huge = [(x2, y2) 
                                 for x2 in range(x-1, x+4) for y2 in range(y-1, y+4)
                                 if x2 >= 0 and x2 < field_width and y2>= 0 and y2 < field_height and \
                                 not((x2 == x or x2 == x+1 or x2 == x+2) and (y2 == y or y2 == y+1 or y2 == y+2))]
                                 
         
         s.add(field[y][x]["small_tree"] == count_propositions(s, f"small_tree_{x},{y}", 
                                                               [field[y2][x2]["kind"] == META_ID["tree"]
                                                                for x2, y2 in squares_in_range_small]))
         s.add(field[y][x]["big_tree"] == count_propositions(s, f"big_tree_{x},{y}", 
                                                               [field[y2][x2]["kind"] == META_ID["tree"]
                                                                for x2, y2 in squares_in_range_big]))
         s.add(field[y][x]["huge_tree"] == count_propositions(s, f"huge_tree_{x},{y}", 
                                                               [field[y2][x2]["kind"] == META_ID["tree"]
                                                                for x2, y2 in squares_in_range_huge]))
   
         #value houses
         # no income for empty, road, tree, visa and extensions of big houses (to avoid double counting)
         s.add(z3.Implies(
            z3.Or(
               field[y][x]["kind"] < 4, 
               z3.And(
                  field[y][x]["kind"] >= big_house_TR_begin,
                  field[y][x]["kind"] < big_house_BR_end
               ),
               field[y][x]["kind"] >= huge_house_TR_begin,
            ),
            field[y][x]["value"] == 0
         ))
         # income small houses
         for i, name in enumerate(houses_by_size["small"]):
            house_idx = begin_small_houses + i
            h_data = HOUSE[name]
            for num_trees in range(len(squares_in_range_small)+1):
               s.add(z3.Implies(
                  z3.And(field[y][x]["kind"] == house_idx, field[y][x]["small_tree"] == num_trees),
                  field[y][x]["value"] == 60 * final_passenger_yields(HOUSE[name]["passengers"], num_trees) / HOUSE[name]["time"]
               ))

         # income big houses
         for i, name in enumerate(houses_by_size["big"]):
            house_idx = big_house_TL_begin + i
            for num_trees in range(len(squares_in_range_big)+1):
               s.add(z3.Implies(
                  z3.And(field[y][x]["kind"] == house_idx, field[y][x]["big_tree"] == num_trees),
                  field[y][x]["value"] == math.ceil(60 * final_passenger_yields(HOUSE[name]["passengers"], num_trees) / HOUSE[name]["time"])
               ))

         # income huge houses
         for i, name in enumerate(houses_by_size["huge"]):
            house_idx = huge_house_TL_begin + i
            for num_trees in range(len(squares_in_range_huge)+1):
               s.add(z3.Implies(
                  z3.And(field[y][x]["kind"] == house_idx, field[y][x]["huge_tree"] == num_trees),
                  field[y][x]["value"] == math.ceil(60 * final_passenger_yields(HOUSE[name]["passengers"], num_trees) / HOUSE[name]["time"])
               ))

   number_houses = {
      name: z3.Int(f"amount_of_{name}") 
      for name, data in HOUSE.items() 
      if data["passengers"] > 0
   }

   for name, house_var in number_houses.items():
      if name in houses_by_size["small"]:
         target_idx = begin_small_houses + houses_by_size["small"].index(name)
      elif name in houses_by_size["big"]:
         target_idx = big_house_TL_begin + houses_by_size["big"].index(name)
      else:
         target_idx = huge_house_TL_begin + houses_by_size["huge"].index(name)

      s.add(house_var == z3.Sum([z3.If(field[y][x]["kind"] == target_idx, 1, 0) for x in range(field_width) for y in range(field_height)]))
      s.add(house_var <= 1)

   total_value = z3.Int("total income")
   s.add(total_value == sum([field[y][x]["value"] for x in range(field_width) for y in range(field_height)]))

   #s.add(total_value >= 802)
   # 490 Max!! for non-special houses
   # 802 Max!! for special houses
   
   h_opt = s.maximize(total_value)

   success = s.check()
   if success == z3.sat:
      m = s.model()
      result = s.lower(h_opt)
      print(f"INFO - Final score: {result}")
      translated_field = [[(m.evaluate(field[y][x]["kind"]).as_long(),
                            m.evaluate(field[y][x]["small_tree"]).as_long(),
                            m.evaluate(field[y][x]["big_tree"]).as_long(),
                            m.evaluate(field[y][x]["huge_tree"]).as_long(),
                            str(m.evaluate(field[y][x]["has_visa"])),
                            m.evaluate(field[y][x]["value"]).as_long()) for x in range(field_width)] for y in range(field_height)]

      for i, name in enumerate(houses_by_size["small"]):
         id_to_name[begin_small_houses + i] = name
          
      for i, name in enumerate(houses_by_size["big"]):
         # Map all 4 parts of the big house to the same name
         id_to_name[big_house_TL_begin + i] = name
         id_to_name[big_house_TR_begin + i] = "filler"
         id_to_name[big_house_BL_begin + i] = "filler"
         id_to_name[big_house_BR_begin + i] = "filler"

      for i, name in enumerate(houses_by_size["huge"]):
         # Map all 9 parts of the huge house to the same name
         id_to_name[huge_house_TL_begin + i] = name
         id_to_name[huge_house_TR_begin + i] = "filler"
         id_to_name[huge_house_BL_begin + i] = "filler"
         id_to_name[huge_house_BR_begin + i] = "filler"

      return True, result, translated_field
   else:
      return False, None

#run_z3_solver()
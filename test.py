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

def final_passenger_yields(passenger, num_trees):
    boosted = passenger * (1 + 0.1 * num_trees)
    return math.ceil(boosted) 

HOUSE = {
      "empty" :                { "passengers":   0, "time":    0, "size": 1 },
      "visa" :                 { "passengers":   0, "time":    0, "size": 1 },
      "road" :                 { "passengers":   0, "time":    0, "size": 1 },
      "tree" :                 { "passengers":   0, "time":    0, "size": 1 },
      "cottage" :              { "passengers":   1, "time":    1, "size": 1 },
      "side_wing" :            { "passengers":   2, "time":    2, "size": 1 },
      "townhouse" :            { "passengers":   8, "time":   10, "size": 1 },
      "futuristic_house" :     { "passengers":   8, "time":   20, "size": 1 },
      "brickhouse" :           { "passengers":   5, "time":    2, "size": 1 },
      "mansion" :              { "passengers":  12, "time":   20, "size": 2 },
      "stone_castle" :         { "passengers":  36, "time":   60, "size": 2 },
      "manor" :                { "passengers":   9, "time":   15, "size": 2 },
      "house_with_pool" :      { "passengers":  18, "time":   60, "size": 2 },
      "villa" :                { "passengers":  48, "time":  240, "size": 2 },
      "country_house" :        { "passengers":  24, "time":  240, "size": 2 },
      "studio" :               { "passengers":  36, "time":  480, "size": 2 },
      "bearing_Wall_house" :   { "passengers":  48, "time": 1080, "size": 2 },
      "round_house" :          { "passengers":  57, "time": 1440, "size": 2 },
      "tower_building" :       { "passengers":  63, "time": 2880, "size": 2 },
      "loft" :                 { "passengers":  72, "time": 1440, "size": 2 },
      "square_house" :         { "passengers":  57, "time":  480, "size": 2 },
      "mirror_house" :         { "passengers":  96, "time":  720, "size": 2 },
      "emerald_house" :        { "passengers":  99, "time":  720, "size": 2 },
      "modular_house" :        { "passengers":  67, "time":  360, "size": 2 },
      "acute_house" :          { "passengers": 102, "time":  720, "size": 2 },
      "apartment_hotel" :      { "passengers": 300, "time": 2880, "size": 2 },
      "apartment_house" :      { "passengers":  60, "time":  240, "size": 2 },
      "smart_house" :          { "passengers":  18, "time":   30, "size": 2 },
      "house_of_disturbence" : { "passengers":  85, "time": 1200, "size": 2 },
      "fall_mansion" :         { "passengers":   9, "time":    5, "size": 2 },
      "rural_life_restaurant": { "passengers":  10, "time":   10, "size": 2 },
      "turf_house" :           { "passengers":   3, "time":    5, "size": 2 },
      "multistory_building" :  { "passengers":  56, "time":  240, "size": 3 },
      "loft_condominium" :     { "passengers":  96, "time":  480, "size": 3 },
      "condominium" :          { "passengers": 190, "time": 1440, "size": 3 },
   }

id_to_name = {0: "empty", 1: "visa", 2: "road", 3: "tree"}

def run_z3_solver():
   field_width = 9
   field_height = 9
   visa_locs = [(4, 4)]
   visa_range = 1

   meta_keys = ["empty", "visa", "road", "tree"]
   # Dynamic ID mapping for meta keys
   META_ID = {name: i for i, name in enumerate(meta_keys)}

   houses_by_size = {
      "small": [n for n, d in HOUSE.items() if d["size"] == 1 and n not in meta_keys],
      "big":   [n for n, d in HOUSE.items() if d["size"] == 2 and n not in meta_keys],
      "huge":  [n for n, d in HOUSE.items() if d["size"] == 3 and n not in meta_keys]
   }

   # ID range calculations
   begin_small_houses = 4
   end_small_houses = begin_small_houses + len(houses_by_size["small"])

   big_house_TL_begin = end_small_houses
   big_house_TL_end   = big_house_TL_begin + len(houses_by_size["big"])
   big_house_TR_begin = big_house_TL_end
   big_house_TR_end   = big_house_TR_begin + len(houses_by_size["big"])
   big_house_BL_begin = big_house_TR_end
   big_house_BL_end   = big_house_BL_begin + len(houses_by_size["big"])
   big_house_BR_begin = big_house_BL_end
   big_house_BR_end   = big_house_BR_begin + len(houses_by_size["big"])

   huge_house_TL_begin = big_house_BR_end
   huge_house_TL_end   = huge_house_TL_begin + len(houses_by_size["huge"])
   huge_house_TR_begin = huge_house_TL_end
   huge_house_TR_end   = huge_house_TR_begin + len(houses_by_size["huge"])
   huge_house_BL_begin = huge_house_TR_end
   huge_house_BL_end   = huge_house_BL_begin + len(houses_by_size["huge"])
   huge_house_BR_begin = huge_house_BL_end
   huge_house_BR_end   = huge_house_BR_begin + len(houses_by_size["huge"])

   s = z3.Solver()

   field = [[{
      "kind": z3.Int(f"field_kind_at_{x},{y}"),
      "small_tree": z3.Int(f"trees_nearby_small_at_{x},{y}"),
      "big_tree": z3.Int(f"trees_nearby_big_at_{x},{y}"),
      "huge_tree": z3.Int(f"trees_nearby_huge_at_{x},{y}"),
      "has_visa": z3.Bool(f"has_visa_{x},{y}"),
      "value": z3.Int(f"value_at_{x},{y}")
   } for x in range(field_width)] for y in range(field_height)]

   for y in range(field_height):
      for x in range(field_width):
         if (x, y) in visa_locs:
            s.add(field[y][x]["kind"] == META_ID["visa"])
         else:
            s.add(field[y][x]["kind"] != META_ID["visa"])
            s.add(field[y][x]["kind"] >= 0)
            s.add(field[y][x]["kind"] < huge_house_BR_end)

   # Big house structural integrity
   for y in range(field_height):
      for x in range(field_width):
         s.add(z3.Implies(
               z3.And(field[y][x]["kind"] >= big_house_TL_begin, field[y][x]["kind"] < big_house_TL_end),
               z3.And(
                  field[y][x+1]["kind"] - big_house_TR_begin == field[y][x]["kind"]-big_house_TL_begin if x+1 < field_width else False,
                  field[y+1][x]["kind"] - big_house_BL_begin == field[y][x]["kind"]-big_house_TL_begin if y+1 < field_height else False,
                  field[y+1][x+1]["kind"]-big_house_BR_begin == field[y][x]["kind"]-big_house_TL_begin if x+1 < field_width and y+1 < field_height else False
               )
         ))
         s.add(z3.Implies(
            z3.And(field[y][x]["kind"] >= big_house_TR_begin, field[y][x]["kind"] < big_house_TR_end),
            field[y][x-1]["kind"] - big_house_TL_begin == field[y][x]["kind"] - big_house_TR_begin if x-1 >= 0 else False
         ))
         s.add(z3.Implies(
            z3.And(field[y][x]["kind"] >= big_house_BL_begin, field[y][x]["kind"] < big_house_BL_end),
            field[y-1][x]["kind"] - big_house_TL_begin == field[y][x]["kind"] - big_house_BL_begin if y-1 >= 0 else False
         ))
         s.add(z3.Implies(
            z3.And(field[y][x]["kind"] >= big_house_BR_begin, field[y][x]["kind"] < big_house_BR_end),
            field[y-1][x-1]["kind"] - big_house_TL_begin == field[y][x]["kind"] - big_house_BR_begin if x-1 >= 0 and y-1 >= 0 else False
         ))

   # Huge house structural integrity
   for y in range(field_height):
      for x in range(field_width):
         s.add(z3.Implies(
               z3.And(field[y][x]["kind"] >= huge_house_TL_begin, field[y][x]["kind"] < huge_house_TL_end),
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
         ))
         # Simplified checks for parts checking back to TL
         s.add(z3.Implies(z3.And(field[y][x]["kind"] >= huge_house_TR_begin, field[y][x]["kind"] < huge_house_TR_end),
            z3.Or(field[y][x-1]["kind"] - huge_house_TL_begin == field[y][x]["kind"] - huge_house_TR_begin if x-1 >= 0 else False,
                  field[y][x-2]["kind"] - huge_house_TL_begin == field[y][x]["kind"] - huge_house_TR_begin if x-2 >= 0 else False)))
         
   # Road connectivity constraints
   for y in range(field_height):
      for x in range(field_width):
         road_id = META_ID["road"]
         # Small houses + Visa road check
         s.add(z3.Implies(
            z3.Or(field[y][x]["kind"] == META_ID["visa"], z3.And(field[y][x]["kind"] >= begin_small_houses, field[y][x]["kind"] < end_small_houses)),
            z3.Or(field[y-1][x]["kind"] == road_id if y-1 >= 0 else False, field[y+1][x]["kind"] == road_id if y+1 < field_height else False,
                  field[y][x-1]["kind"] == road_id if x-1 >= 0 else False, field[y][x+1]["kind"] == road_id if x+1 < field_width else False)))

   # Visa Range Logic
   for y in range(field_height):
      for x in range(field_width):
         square_range = [(x2, y2) for x2 in range(x-visa_range, x+visa_range+1) for y2 in range(y-visa_range, y+visa_range+1)
                         if 0 <= x2 < field_width and 0 <= y2 < field_height and not(x2 == x and y2 == y)]
         s.add(field[y][x]["has_visa"] == z3.Or([field[y2][x2]["kind"] == META_ID["visa"] for x2, y2 in square_range]))

   # Tree count logic
   tree_id = META_ID["tree"]
   for y in range(field_height):
      for x in range(field_width):
         # ... [Keep your existing squares_in_range calculations] ...
         squares_in_range_small = [(x2, y2) for x2 in range(x-1, x+2) for y2 in range(y-1, y+2) if 0 <= x2 < field_width and 0 <= y2 < field_height and not(x2 == x and y2 == y)]
         s.add(field[y][x]["small_tree"] == count_propositions(s, f"st_{x}_{y}", [field[y2][x2]["kind"] == tree_id for x2, y2 in squares_in_range_small]))

   # Value Logic
   for y in range(field_height):
      for x in range(field_width):
         # No income for meta types or non-top-left parts of multi-tile houses
         s.add(z3.Implies(z3.Or(field[y][x]["kind"] < 4, 
                               z3.And(field[y][x]["kind"] >= big_house_TR_begin, field[y][x]["kind"] < big_house_BR_end),
                               field[y][x]["kind"] >= huge_house_TR_begin),
                          field[y][x]["value"] == 0))

         # Small House Income
         for i, name in enumerate(houses_by_size["small"]):
            h_idx = begin_small_houses + i
            h_data = HOUSE[name]
            for nt in range(9):
                s.add(z3.Implies(z3.And(field[y][x]["kind"] == h_idx, field[y][x]["small_tree"] == nt),
                                 field[y][x]["value"] == int(60 * final_passenger_yields(h_data["passengers"], nt) / h_data["time"])))

         # Big House Income (at TL)
         for i, name in enumerate(houses_by_size["big"]):
            h_idx = big_house_TL_begin + i
            h_data = HOUSE[name]
            # Use big_tree count for value calculation
            s.add(z3.Implies(field[y][x]["kind"] == h_idx, 
                             field[y][x]["value"] == int(60 * final_passenger_yields(h_data["passengers"], 0) / h_data["time"]))) # Simplified for demo

         for i, name in enumerate(houses_by_size["huge"]):
            h_idx = huge_house_TL_begin + i
            h_data = HOUSE[name]
            for nt in range(25): # Huge houses can have up to 24 trees in range
                income_val = math.ceil(60 * final_passenger_yields(h_data["passengers"], nt) / h_data["time"])
                s.add(z3.Implies(
                    z3.And(field[y][x]["kind"] == h_idx, field[y][x]["huge_tree"] == nt),
                    field[y][x]["value"] == income_val
                ))

   # Counting quantities
   number_houses = {name: z3.Int(f"amt_{name}") for name, d in HOUSE.items() if d["passengers"] > 0}
   for name, house_var in number_houses.items():
      # Determine the TL index for this specific house
      if name in houses_by_size["small"]:
         target_idx = begin_small_houses + houses_by_size["small"].index(name)
      elif name in houses_by_size["big"]:
         target_idx = big_house_TL_begin + houses_by_size["big"].index(name)
      else:
         target_idx = huge_house_TL_begin + houses_by_size["huge"].index(name)

      s.add(house_var == z3.Sum([z3.If(field[y][x]["kind"] == target_idx, 1, 0) for x in range(field_width) for y in range(field_height)]))
      s.add(house_var <= 1)

   total_value = z3.Int("total_income")
   s.add(total_value == z3.Sum([field[y][x]["value"] for x in range(field_width) for y in range(field_height)]))
   s.add(total_value >= 400) # Adjusted for testing
   
   success = s.check()
   if success == z3.sat:
      m = s.model()
      print(m.evaluate(total_value).as_long())
      translated_field = []
      for y in range(field_height):
          row = []
          for x in range(field_width):
              # evaluate() can return an ArithRef; calling as_long() requires a concrete value.
              # We use m.evaluate(..., model_completion=True) to force a choice if the solver is indifferent.
              kind = m.evaluate(field[y][x]["kind"], model_completion=True).as_long()
              st   = m.evaluate(field[y][x]["small_tree"], model_completion=True).as_long()
              bt   = m.evaluate(field[y][x]["big_tree"], model_completion=True).as_long()
              ht   = m.evaluate(field[y][x]["huge_tree"], model_completion=True).as_long()
              visa = str(m.evaluate(field[y][x]["has_visa"], model_completion=True))
              val  = m.evaluate(field[y][x]["value"], model_completion=True).as_long()
              
              row.append((kind, st, bt, ht, visa, val))
          translated_field.append(row)

      
      
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

      for y in range(field_height):
          print([k for k, _, _, _, _, _ in translated_field[y]], sep=", ")

      return True, translated_field
   else:
      return False, None

#run_z3_solver()
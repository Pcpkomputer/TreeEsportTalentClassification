def findDecision(obj): #obj[0]: experience, obj[1]: skill, obj[2]: intellegence, obj[3]: attitude, obj[4]: turnamen
   # {"feature": "turnamen", "instances": 145, "metric_value": 0.8299, "depth": 1}
   if obj[4] == 'tidak':
      # {"feature": "experience", "instances": 142, "metric_value": 0.8056, "depth": 2}
      if obj[0] == 'tidak':
         # {"feature": "intellegence", "instances": 102, "metric_value": 0.4627, "depth": 3}
         if obj[2] == 'tidak':
            # {"feature": "attitude", "instances": 84, "metric_value": 0.1623, "depth": 4}
            if obj[3] == 'tidak':
               return 'tidak diterima'
            elif obj[3] == 'lolos':
               # {"feature": "skill", "instances": 15, "metric_value": 0.5665, "depth": 5}
               if obj[1] == 'lolos':
                  return 'tidak diterima'
               elif obj[1] == 'tidak':
                  return 'tidak diterima'
               else:
                  return 'tidak diterima'
            else:
               return 'tidak diterima'
         elif obj[2] == 'lolos':
            # {"feature": "attitude", "instances": 18, "metric_value": 0.9911, "depth": 4}
            if obj[3] == 'tidak':
               # {"feature": "skill", "instances": 15, "metric_value": 0.9183, "depth": 5}
               if obj[1] == 'lolos':
                  return 'tidak diterima'
               else:
                  return 'tidak diterima'
            elif obj[3] == 'lolos':
               return 'diterima'
            else:
               return 'diterima'
         else:
            return 'tidak diterima'
      elif obj[0] == 'lolos':
         # {"feature": "attitude", "instances": 40, "metric_value": 0.9544, "depth": 3}
         if obj[3] == 'tidak':
            # {"feature": "skill", "instances": 26, "metric_value": 0.9829, "depth": 4}
            if obj[1] == 'lolos':
               # {"feature": "intellegence", "instances": 16, "metric_value": 0.896, "depth": 5}
               if obj[2] == 'tidak':
                  return 'diterima'
               elif obj[2] == 'lolos':
                  return 'diterima'
               else:
                  return 'diterima'
            elif obj[1] == 'tidak':
               return 'tidak diterima'
            else:
               return 'tidak diterima'
         elif obj[3] == 'lolos':
            return 'diterima'
         else:
            return 'diterima'
      else:
         return 'diterima'
   elif obj[4] == 'lolos':
      return 'diterima'
   else:
      return 'diterima'

def findDecision(obj): #obj[0]: experience, obj[1]: skill, obj[2]: intellegence, obj[3]: attitude, obj[4]: turnamen
   # {"feature": "turnamen", "instances": 121, "metric_value": 0.8882, "depth": 1}
   if obj[4] == 'tidak':
      # {"feature": "experience", "instances": 118, "metric_value": 0.8663, "depth": 2}
      if obj[0] == 'tidak':
         # {"feature": "intellegence", "instances": 85, "metric_value": 0.5226, "depth": 3}
         if obj[2] == 'tidak':
            # {"feature": "attitude", "instances": 70, "metric_value": 0.1872, "depth": 4}
            if obj[3] == 'tidak':
               return 'tidak diterima'
            elif obj[3] == 'lolos':
               # {"feature": "skill", "instances": 11, "metric_value": 0.684, "depth": 5}
               if obj[1] == 'lolos':
                  return 'tidak diterima'
               elif obj[1] == 'tidak':
                  return 'tidak diterima'
               else:
                  return 'tidak diterima'
            else:
               return 'tidak diterima'
         elif obj[2] == 'lolos':
            # {"feature": "attitude", "instances": 15, "metric_value": 0.9968, "depth": 4}
            if obj[3] == 'tidak':
               # {"feature": "skill", "instances": 11, "metric_value": 0.9457, "depth": 5}
               if obj[1] == 'lolos':
                  return 'tidak diterima'
               else:
                  return 'tidak diterima'
            elif obj[3] == 'lolos':
               return 'diterima'
            else:
               return 'diterima'
         else:
            return 'diterima'
      elif obj[0] == 'lolos':
         # {"feature": "attitude", "instances": 33, "metric_value": 0.8454, "depth": 3}
         if obj[3] == 'tidak':
            # {"feature": "skill", "instances": 19, "metric_value": 0.998, "depth": 4}
            if obj[1] == 'lolos':
               # {"feature": "intellegence", "instances": 12, "metric_value": 0.65, "depth": 5}
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

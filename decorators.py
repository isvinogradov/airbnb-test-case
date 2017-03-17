# coding: utf-8
import re

def validate(constraints):
    def inner1(f):
        def inner2(instance, *args, **kwargs):
            errors = 0
            reason = ''
            for par in constraints:
                parameter_name = par['parameter_name']
                type_ = par.get('type', None)
                required = par.get('required', None)
                default = par.get('default', None)
                min_ = par.get('min', None)
                max_ = par.get('max', None)
                regex = par.get('regex', None)
                
                parameter_val = instance.get_argument(parameter_name, None)
                if required and not parameter_val:
                    errors += 1
                    reason = 'parameter «%s» is required' % parameter_name
                    break
                
                if not required and not parameter_val:
                    setattr(instance, parameter_name, default)
                    continue
                    
                if regex:
                    ptrn_compiled = re.compile(regex)
                    if not ptrn_compiled.match(parameter_val):
                        errors += 1
                        reason = 'regex check «%s» failed against parameter «%s»' % (parameter_name, regex)
                        break
                
                if type_:    
                    try:
                        parameter_val = type_(parameter_val)
                    except ValueError:
                        errors += 1
                        reason = 'parameter «%s» expected type: %s' % (parameter_name, type_.__name__)
                        break
                    
                    if any([type_ is int, type_ is float]):
                        if min_:
                            if not (min_ <= parameter_val):
                                errors += 1
                                reason = 'parameter «%s» value is too small' % parameter_name
                                break
                        if max_:
                            if not (parameter_val <= max_):
                                errors += 1
                                reason = 'parameter «%s» value is too big' % parameter_name
                                break
                        
                setattr(instance, parameter_name, parameter_val)
                
            if not errors:
                return f(instance, *args, **kwargs)
            else:
                instance.set_status(400)
                instance.write(reason)
                instance.finish()
                return
                
        return inner2
    return inner1
from cosu import utils
from csip import Client
from typing import List, Dict, Tuple
import queue, os


def csip_worker(reqq: queue.Queue, thread_no: int, stop, full_trace,
                url, files, arg_params, conf: Dict, metainfo: Dict) -> None:
    async_call = conf.get('async_call', True)  # default is async
    save_resp = conf.get('save_response_to', None)  # save response, set it to a folder if responses should be saved.

    while not stop():
        try:
            (rnd, step, iteration, particle, x, step_param, calib_params, objfunc, resq) = reqq.get(True, 0.5)
            # print(thread_no, particle)

            c = Client(metainfo=metainfo)

            all_params = {}

            # static params (from args)
            for param in arg_params:
                c.add_data(param['name'], param['value'])

            # particle params  (generated from steps)
            # for i, value in enumerate(x):
            # for idx, value in enumerate(x[particle, :]):
            #     c.add_data(step_param_names[idx], value)
            values = x[particle]
            idx = 0
            for p in step_param:
                value_type = p.get('type', 'float')
                if 'float' == value_type:
                    c.add_data(p['name'], values[idx])
                    all_params[p['name']] = values[idx]
                    idx = idx + 1
                elif 'list' == value_type:
                    base_name = p['name']
                    calibration_strategy = p.get('calibration_strategy', 'mean')

                    if 'mean' == calibration_strategy:
                        mean = values[idx]
                        default_value = p['default_value']
                        value = [(1 + mean) * x for x in default_value]
                        c.add_data(base_name, value)
                        all_params[base_name] = value
                        idx = idx + 1
                    elif 'single' == calibration_strategy:
                        default_value = p['default_value']
                        sub_index = 0
                        value = default_value.copy()
                        while sub_index < len(default_value):
                            value[sub_index] = values[idx]
                            idx = idx + 1
                            sub_index = sub_index + 1
                        c.add_data(base_name, value)
                        all_params[base_name] = value

            # other, previously calibrated params (other steps)
            for name, value in calib_params.items():
                c.add_data(name, value)
                all_params[name] = value

            # objective function info
            for of in objfunc:
                c.add_cosu(of['name'], of['of'], of['data'])
                # c.add_data(of['name'], (of['data'][0], of['data'][1]))

            print('.', end='', flush=True)

            try:
                # print(c)
                if async_call:
                    res = c.execute_async(url, files=files, conf=conf)
                else:
                    res = c.execute(url, files=files, conf=conf)

                # run_string = 'r{}s{}i{}p{}.json'.format(rnd, step, iteration, particle)

                if save_resp:
                    res.save_to(os.path.join(save_resp, 'r{}s{}i{}p{}.json'.format(rnd, step, iteration, particle)))

                if res.is_failed():
                    print(u'F')
                    # print(res)
                    resq.put((particle, 100))
                else:
                    # print(res)
                    # print(u'\u2714', end='', flush=True)
                    print(u'O', end='', flush=True)
                    cost = utils.calc_cost(res, objfunc)
                    resq.put((particle, cost))
                    # break

                if full_trace is not None:
                    full_trace.append((all_params, cost))

                resq.put((particle, cost))
            except:
                print(u'sF')
                resq.put((particle, 100))
                continue

            reqq.task_done()
        except queue.Empty:
            continue

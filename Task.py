import multiprocessing
import timeit
import threading


class Job:
    def __init__(self, function, job_args, job_kwargs):
        self.function = function
        self.job_args = job_args
        self.job_kwargs = job_kwargs

    def do(self):
        self.function(*self.job_args, **self.job_kwargs)


class Task:
    def __init__(self, job, ancestors=None, descendants=None, task_name='unnamed task'):
        super().__init__()
        self.job = job

        if not descendants:
            self.descendants = []

        if not ancestors:
            self.ancestors = []

        self.task_name = task_name

    def do(self):
        if not self.ancestors:
            self.job.do()
            self.on_done()
        else:
            print('Cannot do task with name:', self.task_name)
            print(
                'still waiting for completion of ancestor tasks:',
                [str(task) for task in self.ancestors])

    def on_done(self):
        if not self.descendants:
            print('got no descendants, task path finished!')

        for descendant in self.descendants:
            threading.Thread(
                target=descendant.signal_ancestor_finished,
                args=(self,)).start()

    def add_ancestor(self, ancestor):
        self.ancestors.append(ancestor)

    def add_descendant(self, descendant):
        self.descendants.append(descendant)

    def remove_ancestor(self, ancestor):
        try:
            self.ancestors.remove(ancestor)
        except ValueError as exc:
            print('ancestor', ancestor, 'not in list, cannot be removed from list')
        except AttributeError:
            print('self.ancestors does not behave like a list')
        except Exception as exc:
            print('exception:', exc)

    def remove_descandant(self, descandant):
        try:
            self.descandants.remove(descandant)
        except ValueError as exc:
            print('descandant not in list, cannot be removed from list')
        except AttributeError:
            print('self.descandants does not behave like a list')
        except Exception as exc:
            print('exception:', exc)

    def signal_ancestor_finished(self, ancestor):
        # print(self, 'called from ancestor', ancestor)
        self.remove_ancestor(ancestor)
        self.do()

    def __str__(self):
        return self.task_name

    def print_relatives(self):
        print('relatives of', self.task_name)
        print('ancestors are:')
        for ancestor in self.ancestors:
            print(ancestor, 'with id', id(ancestor))
        print('descendants are:')
        for descendant in self.descendants:
            print(descendant, 'with id', id(descendant))
        print('-----------------------------')


def add_association(ancestor, descendant):
    ancestor.add_descendant(descendant)
    descendant.add_ancestor(ancestor)


def busy_wait_func(duration_in_seconds):
    start_time = timeit.default_timer()
    elapsed = 0
    while elapsed < duration_in_seconds:
        a = 1+1
        elapsed = timeit.default_timer() - start_time
    print('DONE C')


if __name__ == '__main__':
    task_a = Task(
        Job(print, ['DONE', ' A'], {'sep': ''}),
        task_name='Task A')

    task_b = Task(
        Job(print, job_args=['DONE', ' B'], job_kwargs={'sep': ''}),
        task_name='Task B')

    task_c = Task(
        Job(busy_wait_func, [0.5], {}),
        task_name='Task C')

    task_d = Task(
        Job(print, job_args=['DONE', ' D'], job_kwargs={'sep': ''}),
        task_name='Task D')

    task_e = Task(
        Job(print, job_args=['DONE', ' E'], job_kwargs={'sep': ''}),
        task_name='Task E')

    add_association(task_a, task_b)
    add_association(task_a, task_d)

    add_association(task_b, task_c)
    add_association(task_c, task_e)

    add_association(task_d, task_e)

    # a--b--c--e
    #  \-d----/
    task_a.do()

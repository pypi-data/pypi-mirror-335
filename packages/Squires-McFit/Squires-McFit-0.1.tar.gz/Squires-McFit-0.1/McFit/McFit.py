import numpy as np
import matplotlib.pyplot as plt
import corner
from typing import Callable
import progress.bar as prog


def met_hastings(fun_to_samp: Callable[[np.ndarray], float], init_guess: np.ndarray, jump_mag: np.ndarray,num_its: int):
    """Use the metropolis-hastings algorithm to sample a distribution. \n
    :param fun_to_samp: the target distribution to sample. Must take a single vector argument and return a single scalar. \n
    :param init_guess: starting point of the algorithm. Must have the same size as the argument of fun_to_samp.\n
    :param jump_mag: covariance matrix for gaussian random jump. For independent jump directions, use a diagonal matrix. Must be a square array whose width is the size of the argument of fun_to_samp.\n
    :param num_its: number of MCMC iterations\n
    :returns param_tracks: sampled distribution. Each column represents one sample of the distribution and each row represents the track (MCMC iterations) for one parameter of the distribution.\n
    :returns acc_rate: acceptance rate
    """
    N = len(init_guess)
    param_tracks = np.zeros((N,num_its))
    rng = np.random.default_rng()
    jumps = rng.multivariate_normal(np.zeros_like(init_guess),jump_mag,(num_its)).T
    acc_rolls = rng.uniform(size = (num_its))
    param_tracks[:,0] = init_guess
    acceptances = 0
    bar = prog.IncrementalBar("MCMC Progress", max = num_its)
    bar.next()
    for i in range(num_its-1):
        my_params = param_tracks[:,i]
        my_val = fun_to_samp(my_params)
        new_params = my_params + jumps[:,i]
        new_val = fun_to_samp(new_params)
        bar.next()
        if new_val>my_val:
            param_tracks[:,i+1] = new_params
            acceptances += 1
        elif acc_rolls[i]<new_val / my_val:
            param_tracks[:,i+1] = new_params
            acceptances += 1
        else:
            param_tracks[:,i+1] = my_params
    bar.finish()
    return (param_tracks, acceptances/num_its,acc_rolls)

def format_mcmc_output(output_tuple: tuple, burn_in : int = 0, labels : list = [], highlight_vals : list = [],highlight_linespec : list = [], show_vals : bool = False):
    """Format the output of ``met_hastings`` as an N-dimensional corner histogram.\n
    :param output_tuple: the output tuple of ``met_hastings``.\n
    :param burn_in: cutoff value for burn-in removal. Will discard the first ```burn_in``` iterations of the Markov chain.\n
    :param labels: variable labels for corner plot. Tex formatting enabled.\n
    :param highlight_vals: values to highlight on corner plot. Must be formatted as a list of lists with each set of values to highlight as one sublist.\n
    :param highlight_linespec: matplotlib color specification for each set of highlight values.\n
    :param show_vals: show computed values
    """
    tracks = output_tuple[0][:,burn_in:]
    if len(labels) != 0:
        cor = corner.corner(tracks.T, labels = labels,show_titles = show_vals)
    else:
        cor = corner.corner(tracks.T,show_titles = show_vals)
    i = 0
    for col in highlight_vals:
        corner.overplot_lines(cor,col,color = highlight_linespec[i])
        i += 1

def chisq_fun(fitfun : Callable[[np.ndarray,np.ndarray],np.ndarray], eval_mesh : np.ndarray, truth : np.ndarray, uncertainty : np.ndarray):
    return lambda pars : np.exp(-np.sum(((fitfun(eval_mesh,pars)-truth)/uncertainty)**2))

def mcmc_fit(fitfun : Callable[[np.ndarray,np.ndarray],np.ndarray], eval_mesh : np.ndarray, truth : np.ndarray, init_guess: np.ndarray,
             uncertainty : np.ndarray = None, jump_mag: np.ndarray = None,num_its: int = 1000,
             burn_in : int = 0, labels : list = [], highlight_vals : list = [],highlight_linespec : list = [], show_vals : bool = True, plot_fit : bool = True):
    """ Use a Metropolis-Hastings algorithm to fit a specified fit function to experimental data
    :param fitfun: function to fit. The first argument is the evaluation mesh and the second is the fit parameter vector
    :param eval_mesh: set of _x_ values to fit to
    :param truth: set of _y_ values to fit to
    :param init_guess: starting point of the algorithm. Must have the same size as the argument of fun_to_samp.\n
    :param jump_mag: covariance matrix for gaussian random jump. For independent jump directions, use a diagonal matrix. Must be a square array whose width is the size of the argument of fun_to_samp.\n
    :param num_its: number of MCMC iterations\n
    :param burn_in: cutoff value for burn-in removal. Will discard the first ```burn_in``` iterations of the Markov chain.\n
    :param labels: variable labels for corner plot. Tex formatting enabled.\n
    :param highlight_vals: values to highlight on corner plot. Must be formatted as a list of lists with each set of values to highlight as one sublist.\n
    :param highlight_linespec: matplotlib color specification for each set of highlight values.\n
    :param show_vals: show computed values\n
    :param plot_fit: if True, plots true data (points) and fit curve (line)
    """
    if uncertainty is None:
        uncertainty = np.ones_like(truth)
    if jump_mag is None:
        jump_mag = np.diag(init_guess/7)
    chisq = chisq_fun(fitfun,eval_mesh,truth,uncertainty)
    par_tracks, acc_rate = met_hastings(chisq,init_guess,jump_mag,num_its)
    covariance = np.cov(par_tracks[:,burn_in:])
    fit_vals = np.median(par_tracks,1)
    format_mcmc_output((par_tracks,acc_rate),burn_in,labels,highlight_vals,highlight_linespec,show_vals)
    plt.show()
    plt.scatter(eval_mesh,truth,label = "Data")
    plt.plot(eval_mesh, fitfun(eval_mesh,fit_vals),label = "Fit")
    plt.show()
    return (fit_vals,covariance)

def test_fun(X):
    x = X[0]
    y = X[1]
    exponent = (x - 1)**2 + (y+2)**2
    exponent_2 = (x - 4)**2 + (y-0)**2
    return np.exp(-exponent) + 2 * np.exp(-exponent_2)
def fit_test(x,pars):
    m = pars[0]
    b = pars[1]
    return m*x+b
#jumparr = np.diag([0.5,0.5])
#numits = 10000
#initguess = [0,0]
#tracks, accs, rolls = met_hastings(test_fun,initguess,jumparr,numits)
#format_mcmc_output((tracks,accs),highlight_vals=[[1,-2],[0,0]],highlight_linespec=["b","r"], labels = [r"$x$", r"$y$"], show_vals = True)
#plt.show()
#print(accs)
""""
jumparr = np.diag([0.5,0.5])
numits = 100000
initguess = [ 0, 0]
x = np.linspace(0,10,200)
m0 = 1
b0 = -1
y_true = m0 * x + b0
y_obs = y_true + 0*np.random.randn(200)
def likelihood(pars):
    m = pars[0]
    b = pars[1]
    y_exp = m*x+b
    err = np.sqrt(np.abs(y_obs))
    chi_squared = ((y_obs - y_exp)/err)**2
    return np.exp(-np.sum(chi_squared))
tracks, accs, rolls = met_hastings(likelihood,initguess,jumparr,numits)
print(accs)
print(np.mean(tracks[:,200:],1))
plt.plot(tracks.T)
plt.show()""" 
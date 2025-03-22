from joblib import Parallel, delayed
from sklearn.utils.validation import check_is_fitted
from gudhi.representations.vector_methods import PersistenceImage
from skimage import filters
from . import hlpr as _dh
from tqdm import tqdm
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
import numpy as np
import pickle
import time

class TrivialImageError(Exception):
    pass

class HomologyError(Exception):
    "Raised when homology for a given dimension is insufficient for calculating some quantity"
    pass

class VidPol:
    """
    Superclass for ImageSeries and ImageSeriesPlus classes
    """
    def __init__(self, video, polygon=None, div=1, n_jobs=None):
        if video.ndim == 2:
            video = np.expand_dims(video, axis=0)    
        elif video.ndim != 3: 
            raise ValueError("Need to initialize with array of 2 or 3 dimensions")
        
        if div==1:
            self.video = video     
        elif div <= 0:
            raise ValueError("div argument cannot be 0 or less")
        else: 
            self.video = np.rint(video/div)
            
        if np.any([np.all(np.isclose(im, im[0, 0])) for im in self.video]):
            raise TrivialImageError("""There is an image in the video containing pixels which are all the same intensity. 
                                    If div is not set to 1, try setting div equal to 1.""")
        
        self.polygon = polygon
        self.div = div
        self.n_jobs = n_jobs
           

class ImageSeries(VidPol):
    """
    Reads in an image series (video), either a single or multiple frames. 

    May optionally specify polygonally region, held constant across frames,
    in which to select specific generators in persistent homology.

    Parameters
    ----------
    video : array_like
            Image series. Index on axis=0 represents the frame index, unless a single image (2d array) is provided. 
    polygon : shapely.Polygon, optional, default is ``None``
            Polygonal region outside of which positive cells of 0th persistent homology will be excluded. 
    div : positive int/float, optional, default is ``1``.
            In nanoparticle imaging process, pixel intensities are often registered as something close to a(div), 
            so dividing by div and rounding to nearest integer will give pixel intensities that conform more strongly 
            to common parametric assumptions.
    n_jobs : int or None, optional, default is ``None``
            The number of jobs to use for the computation. ``None`` means 1 unless
            in a :obj:`joblib.parallel_backend` context. ``-1`` means using all
            processors.
    """
    def __init__(self, video, polygon=None, div=1, n_jobs=None):
        super().__init__(video, polygon, div=div, n_jobs=n_jobs)
        self.degp_totp = {}
    
    def fit(self, sigma=None, max_death_pixel_int=True, print_time=True):
        """
        Fit method for ImageSeries object.

        Optional Gaussian smoothing with sigma parameter.

        The argument max_death_pixel_int controls whether or not 
        the maximum death time is the largest pixel value (within an image),
        or the largest finite death time (within an image).
        """
        if print_time:
            tic=time.perf_counter()        
        self.diags_ = Parallel(n_jobs = self.n_jobs)(delayed(_dh.fitsmoo)(im, self.polygon, sigma, 
                                max_death_pixel_int) for im in self.video)    
        if print_time:
            toc=time.perf_counter()
            print(f"Video processed in {toc - tic:0.4f} seconds")
        
        self.sigma_=sigma
        self.max_death_pixel_int_=max_death_pixel_int
        return self
    
    def get_degp_totp(self, p=1, inf=False):
        "Get degree-p total persistence of each image frame from fitted object."
        check_is_fitted(self)
        dgtp = np.fromiter((_dh.degp_totp(x[x[:,3].astype(bool),2], p, inf) for x in self.diags_), float)
        if inf:
            self.degp_totp['inf'] = dgtp
        else:
            self.degp_totp[str(p)] = dgtp

    def get_pers_entr(self, neg=True):    
        """
        Get persistent entropy of each image frame from fitted object. For hypothesis testing
        purposes, the default is negative of the entropy
        """
        check_is_fitted(self)
        self.pers_entr = np.fromiter((_dh.pers_entr(x[x[:,3].astype(bool),2], neg) for x in self.diags_), float)
    
    def get_alps(self):
        "Get ALPS statistic of each image frame from fitted object."
        check_is_fitted(self)
        self.alps = np.fromiter((_dh.alps(x[x[:,3].astype(bool),2]) for x in self.diags_), float)  
        
        
    def plot_im(self, frame, plot_poly=True, plot_pts=True, smooth=True, thr=None, **kwargs):
        """
        Plot an individual frame in the video, with or without the polygonal region superimposed
        """
        
        imd = self.diags_[frame]
        if smooth:
            plim = filters.gaussian(self.video[frame], sigma=self.sigma_, preserve_range=True)
        else:
            plim = self.video[frame]
        
        which_plt = imd[:, 3].astype(bool)
        if thr==None:
            pass
        else:
            over_thr = (imd[:, 2] > thr) #just right over the threshold, not as a proportion...
            which_plt = np.logical_and(over_thr, which_plt)
            
        if plot_pts:
            plt0 = plt.scatter(
                x = imd[which_plt, 0],
                y = imd[which_plt, 1],
				c = imd[which_plt, 2],
				cmap = "autumn",
                **kwargs
			)
            plt.imshow(plim, cmap="gray")
            plt.colorbar(plt0)	
        else:
            plt.imshow(plim, cmap="gray")
			 
        try:
            if plot_poly:
                xs, ys = list(zip(*self.polygon.exterior.coords)) #'unzip' exterior coordinates of a polygon for plotting
                plt.plot(xs,ys, color="cyan")
        except AttributeError:
            print("Must set plot_poly to False if polygon not specified")    

    def alps_plot(self, frames):
        """
        Returns the ALPS plots of up to 4 images in the video taken by ImageSeries.

        Parameters
        ----------
        frames : int or list
            Indices for frames in image series. 

        Raises
        ------
        TypeError
            If type is not int nor list.
        ValueError
            If more than 4 frames are given.

        Returns
        -------
        None.

        """
        
        if type(frames)!=int and type(frames)!=list:
            raise TypeError("Argument `frames` must be of type int or list")
        
        if type(frames)==int:
            frames = [frames]
        elif len(frames) > 4:
            raise ValueError("Can only plot up to 4 frames")
            
        for frame in frames:
            if frame < 0 or frame > self.video.shape[0]:
                raise IndexError("Frame "+str(frame)+" is not in the video")
                
            imd = self.diags_[frame]
            which_plt = imd[:, 3].astype(bool)
            lts = np.array([0]+list(np.sort(imd[which_plt, 2])))
            yax = [np.log(np.sum(lts > l))for l in lts[:-1]]
            plt.step(lts[:-1], yax, where='post', label='Frame '+str(frame+1))
        
        plt.xlabel(r'$\eta =$'+"Persistence lifetime", labelpad=15)
        plt.ylabel(r'$\ln \sum_{(b,d) \in PD} 1\{ d-b > \eta\}$', labelpad=15)
        if len(frames)==1:
            frame_name = str(frames[0]+1)
            plt.title("ALPS plot: frame "+frame_name, pad=15)
        else:
            frame_name = ", ".join(str(frame+1) for frame in frames[:-1])+" and "+str(frames[-1]+1)
            plt.title("ALPS plots: frames "+frame_name, pad=15)
        plt.legend()

class ImageSeriesPlus(VidPol):
    """
    Reads in an image series (video), either a single or multiple frames. 

    May optionally specify polygonal region, held constant across frames,
    in which to select specific generators in persistent homology. Similar to ImageSeries,
    but with enhanced functionality for utilizing BOTH 0- and 1-dimensional persistent homology.
    
    Parameters
    ----------
    video : array_like
            Image series. Index on axis=0 represents the frame index, unless a single image (2d array) is provided. 
    polygon : shapely.Polygon, optional, default is ``None``
            Polygonal region outside of which positive cells of 0th persistent homology will be excluded. 
    div : positive int/float, optional, default is ``1``.
            In nanoparticle imaging process, pixel intensities are often registered as something close to a(div), 
            so dividing by div and rounding to nearest integer will give pixel intensities that conform more strongly 
            to common parametric assumptions.
    n_jobs : int or None, optional, default is ``None``
            The number of jobs to use for the computation. ``None`` means 1 unless
            in a :obj:`joblib.parallel_backend` context. ``-1`` means using all
            processors.
    im_list: bool, defautl is ``False``
            Bool indicating whether or not a list of numpy arrays is given (True) rather than a 3d numpy array.
    """
    def __init__(self, video, polygon=None, div=1, n_jobs=None, im_list=False):
        if im_list:
            self.video = video
            self.n_jobs = n_jobs
            self.polygon=None
            self.div=1
        else:
            super().__init__(video, polygon, div=div, n_jobs=n_jobs)
            self.video = [im for im in self.video]
    
    def fit(self, sigma=None, print_time=True, verbose=0):
            """
            Fit method for ImageSeriesPlus object.

            Optional Gaussian smoothing with sigma parameter.
            """
            if print_time:
                tic=time.perf_counter()
            self.diags_ = Parallel(n_jobs = self.n_jobs, verbose=verbose)(
                                    delayed(_dh.persmoo)(im, self.polygon, sigma) 
                                    for im in self.video)
            
            if print_time:
                toc=time.perf_counter()
                print(f"Images processed in {toc - tic:0.4f} seconds")
            
            self.sigma_=sigma
            return self
        
    def pd_threshold(self, minv, maxv, dim="both", num=50):
        """
        
        Parameters
        ----------
        minv : float
            Minimum threshold to consider.
        maxv : float
            Maximum threshold to consider.
        dim : str or int, optional
            Integer 0 or 1 corresponds to thresholding only based on dimension 0 and 1 persistence features.
            The default is "both", corresponding to both dimensions 0 and 1. 

        Raises
        ------
        HomologyError
           Error raised due to lack of sufficient homology to perform PD thresholding.

        Returns
        -------
        ims_t : list of ndarray. 
            Binary, thresholded images.

        """
        check_is_fitted(self)
        ims_t = []
        for index, im in enumerate(self.video):
            smim = filters.gaussian(im, sigma=self.sigma_, preserve_range=True)
            try:
                thresh = _dh.pd_thresh_calc(self.diags_[index], np.unique(smim), minv, maxv, dim, num)
            except ValueError:
                raise HomologyError("Not enough homology information to calculate threshold for image index "+str(index)) from None
                    
            ims_t.append(np.rint(smim > thresh))
            
        return ims_t
        
    def convert_to_df(self):
        """
        Creates pandas DataFrames (self.dfs) from persistence information calculated from detectda algorithm.

        Returns
        -------
        None.

        """
        check_is_fitted(self)
        col_names = ["x_coord", "y_coord", "hom_dim", "birth", "death", "in_poly"]
        self.dfs = [pd.DataFrame(x, columns=col_names) for x in self.diags_]
    
    def get_lifetimes(self):
        """
        Creates persistence lifetimes (self.lifetimes) for each persistence diagram in image series.

        Returns
        -------
        None.

        """
        check_is_fitted(self)
        lt = lambda pd: pd[:,4] - pd[:,3]
        lt0 = [lt(x[x[:,2]==0,:]) for x in self.diags_]
        lt1 = [lt(x[x[:,2]==1,:]) for x in self.diags_]
        self.lifetimes = [lt0, lt1]
    
    def get_midlife_coords(self):
        """
        Creates persistence midlife coordinates (self.midlife_coords) for each persistence diagram in image series.

        Returns
        -------
        None.

        """
        check_is_fitted(self)
        ml = lambda pd: (pd[:,4]+pd[:,3])/2
        ml0 = [ml(x[x[:,2]==0,:]) for x in self.diags_]
        ml1 = [ml(x[x[:,2]==1,:]) for x in self.diags_]
        self.midlife_coords = [ml0, ml1]
    
    def get_pers_im(self, bts, lts, dim, bandwidth=1):
        """
        Create persistence images from cubical persistent homology for each image in the detectda object,
        for homology dimension dim. The resulting dimension of the persistence image vectorizations is bts x lts.
        

        Parameters
        ----------
        bts : int
            birth-time resolution (higher = finer)
        lts : int
            lifetime resolution (higher = finer).
        bandwidth : float
            Positive number corresponding to Gaussian kernel bandwidth (i.e. variance)
        dim : int
            Integer 0 or 1 corresponds to thresholding only based on dimension 0 and 1 persistence features.

        Returns
        -------
        None.

        """
        if bandwidth <= 0:
            raise ValueError("bandwidth must be positive.")
        
        if dim != 0 and dim != 1:
            raise ValueError("dim must equal 0 or 1")
        
        diags = [d[np.logical_and(d[:,2]==dim, d[:,5]==1),:][:, [3,4]] for d in self.diags_]
        PI_obj = PersistenceImage(bandwidth=bandwidth, weight=_dh.weight_func,
                           resolution = [bts,lts])

        PI_obj.fit(diags)
        self.bts, self.lts = bts, lts
        self.pis = PI_obj.transform(diags)
        #birtt_bd gives the boundaries of the birth times used in the persistence image
        self.birtt_bd = np.linspace(PI_obj.im_range_fixed_[0], PI_obj.im_range_fixed_[1], bts)
        #lifet_bd gives the boundaries of the birth times used in the persistence image
        self.lifet_bd = np.linspace(PI_obj.im_range_fixed_[2], PI_obj.im_range_fixed_[3], lts)
        self.diags_alt_ = [d[np.logical_and(d[:,2]==dim, d[:,5]==1),:][:, [0,1,3,4]] for d in self.diags_]
    
    def get_pers_mag(self):
        """
        Creates persistence magnitudes (self.pers_mag) for each persistence diagram in image series.

        Returns
        -------
        None.

        """
        check_is_fitted(self)
        self.pers_mag = [np.sum((-1)**(x[:,2])*(np.exp(-x[:,3])-np.exp(-x[:,4]))) for x in self.diags_]
    
    def get_pers_stats(self):
        """
        Get persistence statistics for each image, according to `Topological approaches to skin disease analysis`, along with 
            persistent entropy and ALPS statistics, constituting an embedding into 36-dimensional Euclidean space.
        """
        q25 = lambda x: np.quantile(x, 0.25)
        q75 = lambda x: np.quantile(x, 0.75)
        funcs = {'mean': np.mean, 
                 'variance': np.var,
                 'skewness': stats.skew, 
                 'kurtosis': stats.kurtosis, 
                 'median': np.median,
                 'iqr': stats.iqr, 
                 'q25': q25, 
                 'q75': q75}
        
        stats_vals = []
        for i, diag in tqdm(enumerate(self.diags_)):
            stats0 = np.array([])
            if i == 0: 
                names = np.array([])
            for dim in [0,1]:
                sub_diag = diag[np.logical_and(diag[:,2]==dim, diag[:,5]==1),:]
                for typ in ['mid', 'life']:
                    if typ == 'mid':
                        typ_diag = (sub_diag[:,4]+sub_diag[:,3])/2
                    else:
                        typ_diag = (sub_diag[:,4]-sub_diag[:,3])
                        stats0 = np.append(stats0, [_dh.pers_entr(typ_diag, neg=False), _dh.alps(typ_diag)])
                        if i == 0: 
                            names = np.append(names, ["pers_entr_"+str(dim)+"_life", "alps_"+str(dim)+"_life"])
                    for name, func in funcs.items(): ####NEED TO FIGURE OUT THE ISSUE HERE...
                        val = func(typ_diag)
                        stats0 = np.append(stats0, val)
                        if i == 0: 
                            names = np.append(names, "_".join([name, str(dim), typ]))
            stats_vals = np.append(stats_vals, stats0)
        
        
        stats_df = np.reshape(stats_vals, (len(self.diags_), len(names)))
        return pd.DataFrame(stats_df, columns=names)
    
    def plot_im(self, frame, dim=0, plot_poly=True, plot_pts=True, smooth=True, thr=None, **kwargs):
        """
        Plot an individual frame in the video, with or without the polygonal region superimposed
        """
        
        imd_ = self.diags_[frame]
        imd = imd_[imd_[:,2]==dim, :]
            
        if smooth:
            plim = filters.gaussian(self.video[frame], sigma=self.sigma_, preserve_range=True)
        else:
            plim = self.video[frame]
        
        which_plt = imd[:, 5].astype(bool)
        if thr==None:
            pass
        else:
            if not hasattr(self, 'lifetimes'):
                self.get_lifetimes()
            
            over_thr = (self.lifetimes[dim][frame] > thr) #just right over the threshold, not as a proportion...
            which_plt = np.logical_and(over_thr, which_plt)
            
        lt = imd[which_plt, 4]-imd[which_plt, 3]
        if plot_pts:
            if dim==0:
                cm = "autumn"
            else:
                cm = "Wistia"
            plt0 = plt.scatter(
                x = imd[which_plt, 0],
                y = imd[which_plt, 1],
				c = lt,
				cmap = cm,
                **kwargs
			)
            plt.imshow(plim, cmap="gray")
            plt.colorbar(plt0)	
        else:
            plt.imshow(plim, cmap="gray")
			 
        try:
            if plot_poly:
                xs, ys = list(zip(*self.polygon.exterior.coords)) #'unzip' exterior coordinates of a polygon for plotting
                plt.plot(xs,ys, color="cyan")
        except AttributeError:
            print("Must set plot_poly to False if polygon not specified")
            
    def proc_pers_im(self, betas, quantiles, indices):
        """

        Parameters
        ----------
        betas : array-like of shape (n_samples, n_features)
            Simulated values of beta, such as those contained in self.post_beta 
            after running fit and transform methods in bclr class. 
        quantiles : array-like of shape (2,)
            Quantiles which must be greater (resp. less) than 0
            for positive and negative coefficients.
        indices : array-like of shape (n_indices,)
            Which frames to consider for processing. 
        Returns
        -------
        None.

        """
        high_pi = np.where(np.quantile(betas, quantiles[0], axis=0) > 0)[0]
        low_pi = np.where(np.quantile(betas, quantiles[1], axis=0) < 0)[0]
        
        try:
            ijs_hi = [(k // self.bts, k % self.bts) for k in high_pi]
            ijs_low = [(k // self.bts, k % self.bts) for k in low_pi]

            lb_hi = [(self.lifet_bd[ij[0]], self.birtt_bd[ij[1]]) for ij in ijs_hi]
            lb_low = [(self.lifet_bd[ij[0]], self.birtt_bd[ij[1]]) for ij in ijs_low]

            lt_diff = self.lifet_bd[1]-self.lifet_bd[0]; bt_diff = self.birtt_bd[1]-self.birtt_bd[0]
            self.alts = [np.maximum(_dh.calc_close(self.diags_alt_[i], [lt_diff, bt_diff], lb_hi, 1), 
                                    _dh.calc_close(self.diags_alt_[i], [lt_diff, bt_diff], lb_low, 0.5)) 
                         for i in indices]
            self.indices = indices
            
        except NameError:
            print("Make sure to run get_pers_im method first!")
            
    def plot_pi_sig(self, frame, betas_feat='pos', smooth=True, **kwargs):
        """

        Parameters
        ----------
        frame : int
            Frame which you would like to plot. Should lie in self.indices.
        betas_feat : str, optional
            Whether to plot positive, negative betas, or both. 
            The default is 'pos'.
        smooth : bool, optional
            Whether or not to smooth the image. The default is True.
        **kwargs : dict
            Additional parameters for plotting.

        Returns
        -------
        None.

        """
        
        if not hasattr(self, 'indices'):
            raise AttributeError("Run proc_pers_im first.")
        elif frame not in self.indices:
            raise ValueError("Frame does not lie within set of indices for which persistence images have been processed.")

        if smooth:
            plt.imshow(filters.gaussian(self.video[frame], sigma=self.sigma_, preserve_range=True), cmap='gray')
        else:
            plt.imshow(self.video[frame], cmap='gray')
        nr, nc = self.video[frame].shape
        
        fi = np.min(self.indices)
        try:
            xy_hi = self.diags_alt_[frame][:, [0,1]][self.alts[frame-fi] == 1]
            xy_lo = self.diags_alt_[frame][:, [0,1]][self.alts[frame-fi] == 0.5]
        except NameError:
            print("Make sure to run get_pers_im and proc_pers_im first!")
        
        if betas_feat == 'pos':
            plt.scatter(xy_hi[:,0], xy_hi[:,1], color='yellow', **kwargs)
        elif betas_feat == 'neg':
            plt.scatter(xy_lo[:,0], xy_lo[:,1], color='red', **kwargs)
        elif betas_feat == 'both':
            plt.scatter(xy_hi[:,0], xy_hi[:,1], color='yellow', **kwargs)
            plt.scatter(xy_lo[:,0], xy_lo[:,1], color='red', **kwargs)
        
        # Plots frame number on the image appropriately.
        if frame <= 9:
            plt.annotate(str(frame+1), (0.90*nc, 0.95*nr), color='white', size=20, family="Nunito", weight="heavy")
        elif frame <= 99:
            plt.annotate(str(frame+1), (0.85*nc, 0.95*nr), color='white', size=20, family="Nunito", weight="heavy")
        elif frame <= 999:
            plt.annotate(str(frame+1), (0.80*nc, 0.95*nr), color='white', size=20, family="Nunito", weight="heavy")
        elif frame <= 9999:
            plt.annotate(str(frame+1), (0.75*nc, 0.95*nr), color='white', size=20, family="Nunito", weight="heavy")
        else:
            pass
        
        plt.axis("off")

class ImageSeriesPickle(ImageSeries):
    """
    Creates ImageSeries object from .pkl file. Designed for use with output of identify_polygon script.
    """
    def __init__(self, file_path, div=1, n_jobs=None):
        file = open(file_path, 'rb')
        data = pickle.load(file)
        super().__init__(data['video'], data['polygon'], div, n_jobs)
        file.close()
                

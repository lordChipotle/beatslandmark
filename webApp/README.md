# The Hotdog-Not-Hotdog App is running on Fast.ai via [Render](https://render.com)

The app can be accessed via https://hotdog-not-hotdog.onrender.com. Test it out with hotdog-ish looking images!


Take a look at this Colab notebook and see how we created our model:
https://colab.research.google.com/drive/1h_mibPuKCOK0t4XImQQX6zhE5S7tfRkF?usp=sharing#scrollTo=QPJyrnBkrGlf


You can also test changes locally by installing Docker and using the following command:

```
docker build -t fastai-v3 . && docker run --rm -it -p 5000:5000 fastai-v3
```
Never eating the wrong hotdogs again!

django-avatar
=============    

## Modify 修改说明

1.添加height和width选项，只输入一个参数，则就产生一个正方形的头像。    
比如，{% avatar 80 %}，则生成80,80大小的头像。传入两个参数，则会产生对应width和height的头像，比如{% avatar 80,90 %}      

2.在invalid_cache的时候，去settings.py查看要在缓存内删除的头像大小。原版本是只删除一个，就是内置，的大小，比如内置大小是
80,80，则invalid_cache只删除了（80,80）大小的缓存。当有多个尺寸的头像的时候，就不能很好的清除缓存了。

这里在settings.py中配置需要删除所有尺寸

`AVATAR_UPDATE_SIZES = [(x1,y1),(x2,y2),...]`     
3.头像在admin页面的显示的一个[小bug](http://blog.csdn.net/a_9884108/article/details/18792107)

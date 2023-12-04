# 看第 12 行

# import matplotlib.pyplot as plt
# from matplotlib import ticker


# def draw_split_y_plot(x, y, split_range=[(0, 5), (10, 30)]):
#     """
#     画 y 轴的断开图线
#     """
#     """
#     问题较多，有空再修，和 x 轴差不多
#     """
#     # If we were to simply plot data, we'd lose most of the interesting
#     # details due to the outliers. So let's 'break' or 'cut-out' the y-axis
#     # into two portions - use the top (ax1) for the outliers, and the bottom
#     # (ax2) for the details of the majority of our data
#     fig, (ax1, ax2, ax3) = plt.subplots(2, 1, sharex=True)
#     fig.subplots_adjust(hspace=0.05)  # adjust space between axes

#     # plot the same data on both axes
#     ax1.plot(x, y)
#     ax2.plot(x, y)

#     # zoom-in / limit the view to different portions of the data
#     part1, part2 = split_range
#     ax1.set_xlim(part1[0], part1[1])  # outliers only
#     ax2.set_xlim(part2[0], part2[1])  # most of the data

#     # hide the spines between ax and ax2
#     ax1.spines.bottom.set_visible(False)
#     ax2.spines.top.set_visible(False)
#     ax1.xaxis.tick_top()
#     ax1.tick_params(labeltop=False)  # don't put tick labels at the top
#     ax2.xaxis.tick_bottom()

#     # Now, let's turn towards the cut-out slanted lines.
#     # We create line objects in axes coordinates, in which (0,0), (0,1),
#     # (1,0), and (1,1) are the four corners of the axes.
#     # The slanted lines themselves are markers at those locations, such that the
#     # lines keep their angle and position, independent of the axes size or scale
#     # Finally, we need to disable clipping.

#     # draw split line
#     d = 0.5  # proportion of vertical to horizontal extent of the slanted line
#     kwargs = dict(
#         marker=[(-1, -d), (1, d)],
#         markersize=12,
#         linestyle="none",
#         color="k",
#         mec="k",
#         mew=1,
#         clip_on=False,
#     )
#     ax1.plot([0, 1], [0, 0], transform=ax1.transAxes, **kwargs)
#     ax2.plot([0, 1], [1, 1], transform=ax2.transAxes, **kwargs)
#     ax3.plot([1, 0], [0, 1], transform=ax2.transAxes, **kwargs)

#     plt.show()


# def draw_split_x_plot(x, y, split_range=[(0, 5), (10, 30), (50, 100)], is_show=False):
#     """
#     画 x 轴的断开图线
#     """
#     """
#     todo: 1. 加入设置 title 的功能
#     todo: 2. 提供输入分块数量，根据分块数量自动分块
#     todo: 3. 优化设置分块范围
#     todo: 4. 加入设置横纵坐标的 label
#     todo: 5. 加入设置非数值型刻度
#     todo: 6. 根据数据的长度自动适应横坐标刻度间隔
#     """
#     fig, (ax1, ax2, ax3) = plt.subplots(1, 3, sharey=True)
#     fig.subplots_adjust(wspace=0.06)  # adjust space between axes

#     # plot the same data on both axes
#     ax1.plot(x, y)
#     ax2.plot(x, y)
#     ax3.plot(x, y)

#     # zoom-in / limit the view to different portions of the data
#     part1, part2, part3 = split_range
#     ax1.set_xlim(part1[0], part1[1])  # outliers only
#     ax2.set_xlim(part2[0], part2[1])  # most of the data
#     ax3.set_xlim(part3[0], part3[1])  # most of the data

#     # hide the spines between ax and ax2
#     ax1.spines["right"].set_visible(False)
#     ax2.spines["left"].set_visible(False)
#     ax2.spines["right"].set_visible(False)
#     ax3.spines["left"].set_visible(False)
#     ax1.yaxis.tick_left()
#     ax2.yaxis.tick_right()
#     ax2.tick_params(right=False)
#     ax3.tick_params(left=False)

#     # draw split line
#     d = 0.5  # proportion of vertical to horizontal extent of the slanted line
#     kwargs = dict(
#         marker=[(-1, -d), (1, d)],
#         markersize=12,
#         linestyle="none",
#         color="k",
#         mec="k",
#         mew=1,
#         clip_on=False,
#     )
#     ax1.plot([1, 1], [1, 0], transform=ax1.transAxes, **kwargs)
#     ax2.plot([0, 0], [1, 0], transform=ax2.transAxes, **kwargs)
#     ax2.plot([1, 1], [1, 0], transform=ax2.transAxes, **kwargs)
#     ax3.plot([0, 0], [1, 0], transform=ax3.transAxes, **kwargs)

#     fig.set_figheight(5)
#     fig.set_figwidth(10)
#     fig.text(0.5, -0.16, "Subject Object Pair", ha="center", fontsize=14)

#     ax1.set_ylabel("mR", fontsize=14)
#     x_list = list(range(len(y)))
#     ax1.set_xticks(x_list[part1[0] : part1[1]], x[part1[0] : part1[1]], rotation=60)
#     ax2.set_xticks(x_list[part2[0] : part2[1]], x[part2[0] : part2[1]], rotation=60)
#     ax3.set_xticks(x_list[part3[0] : part3[1]], x[part3[0] : part3[1]], rotation=60)
#     ax1.xaxis.set_major_locator(ticker.MultipleLocator(8))
#     ax2.xaxis.set_major_locator(ticker.MultipleLocator(22))
#     ax3.xaxis.set_major_locator(ticker.MultipleLocator(8))

#     if is_show:
#         plt.show()

#     return fig, ax1, ax2, ax3


# def sorted_dict(data, key=0, up_or_down=True):
#     """
#     sorted dict by key
#     Args:
#         data (dict): a data dict
#         key (int, optional): choose sorted by key or value, 0 means sorted by key, 1 means value. Defaults to 0.
#         up_or_down (bool, optional): Whether reverse. Defaults to True.

#     Returns:
#         dict: sorted dict
#     """
#     return dict(sorted(data.items(), key=lambda x: x[key], reverse=up_or_down))

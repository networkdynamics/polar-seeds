from datetime import datetime
import collections
import json
import os
import re

from matplotlib import pyplot as plt
import pandas as pd
import tqdm

def main():

    file_hashtags = ['ukraine', 'standwithukraine', 'russia', 'nato', 'putin', 'moscow', 'zelenskyy', 'stopwar', 'stopthewar', 'ukrainewar', 'ww3' \
        'володимирзеленський', 'славаукраїні', 'путінхуйло🔴⚫🇺🇦', 'россия', 'війнавукраїні', 'зеленський', 'нівійні', 'війна', 'нетвойне', \
        'зеленский', 'путинхуйло', 'denazification', 'specialmilitaryoperation', 'africansinukraine', 'putinspeech', 'whatshappeninginukraine']

    this_dir_path = os.path.dirname(os.path.abspath(__file__))
    root_dir_path = os.path.join(this_dir_path, '..', '..')
    data_dir_path = os.path.join(root_dir_path, 'data')

    videos = []
    for hashtag in file_hashtags:
        print(f"Getting hashtag users: {hashtag}")
        file_path = os.path.join(data_dir_path, f"#{hashtag}_videos.json")
        with open(file_path, 'r') as f:
            video_data = json.load(f)

        videos += video_data

    vids_data = [(video['desc'], datetime.fromtimestamp(video['createTime']), [challenge['title'] for challenge in video.get('challenges', [])]) for video in videos]

    NUM_TOP_HASHTAGS = 20

    video_df = pd.DataFrame(vids_data, columns=['desc', 'createtime', 'hashtags'])
    hashtags_df = video_df.explode('hashtags')

    filter_method = 'russiavsukraine'
    if filter_method == 'top':
        top_hashtags_df = hashtags_df.groupby('hashtags')['desc'].count().sort_values(ascending=False).head(NUM_TOP_HASHTAGS)
        top_hashtags = set(top_hashtags_df.index)

        filtered_hashtags_df = hashtags_df[hashtags_df['hashtags'].isin(top_hashtags)]

    elif filter_method == 'russiavsukraine':
        russiavukraine_words = ['зеленский', 'путинхуйло', 'зеленський', 'путінхуйло']
        russiavukraine = [f"#{word}" for word in russiavukraine_words]
        filtered_hashtags_df = hashtags_df[hashtags_df['hashtags'].isin(russiavukraine)]

    df = filtered_hashtags_df.groupby(['hashtags', pd.Grouper(key='createtime', freq='W')]) \
       .count() \
       .reset_index() \
       .sort_values('createtime')

    start_date = datetime(2022, 1, 1)
    end_date = datetime(2022, 12, 1)

    df = df[df['createtime'] > start_date]
    df = df[df['createtime'] < end_date]

    df = df.pivot_table(index=['createtime'], columns=['hashtags'], fill_value=0).droplevel(0, axis=1)

    df.plot()

    fig_dir_path = os.path.join(root_dir_path, 'figs')
    fig_path = os.path.join(fig_dir_path, 'hashtags_over_time.png')
    plt.savefig(fig_path)


if __name__ == '__main__':
    main()
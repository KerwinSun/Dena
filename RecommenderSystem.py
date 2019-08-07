import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import turicreate
from surprise import NormalPredictor
from surprise import Dataset
from surprise import Reader
from surprise.model_selection import cross_validate
from surprise import SVD
from collections import defaultdict

def predict(ratings, similarity, type='user'):
    if type == 'user':
        mean_user_rating = ratings.mean(axis=1)
        #We use np.newaxis so that mean_user_rating has same format as ratings
        ratings_diff = (ratings - mean_user_rating[:, np.newaxis])
        pred = mean_user_rating[:, np.newaxis] + similarity.dot(ratings_diff) / np.array([np.abs(similarity).sum(axis=1)]).T
    elif type == 'item':
        pred = ratings.dot(similarity) / np.array([np.abs(similarity).sum(axis=1)])
    return pred

def get_top_n(predictions, n=10):
    '''Return the top-N recommendation for each user from a set of predictions.

    Args:
        predictions(list of Prediction objects): The list of predictions, as
            returned by the test method of an algorithm.
        n(int): The number of recommendation to output for each user. Default
            is 10.

    Returns:
    A dict where keys are user (raw) ids and values are lists of tuples:
        [(raw item id, rating estimation), ...] of size n.
    '''

    # First map the predictions to each user.
    top_n = defaultdict(list)
    for uid, iid, true_r, est, _ in predictions:
        top_n[uid].append((iid, est))

    # Then sort the predictions for each user and retrieve the k highest ones.
    for uid, user_ratings in top_n.items():
        user_ratings.sort(key=lambda x: x[1], reverse=True)
        top_n[uid] = user_ratings[:n]

    return top_n




r_cols = ['user_id', 'item_id', 'rating']
ratings = pd.read_csv('user-id-sentiment-category_and_score', names=r_cols)
items = pd.read_csv('item-id', names=['item_id', 'item_name', 'placeholder'])
users = pd.read_csv('user-id',names=['user_id', 'user_name', 'twitter_id'])
n_items = ratings.item_id.unique().shape[0]
n_users = ratings.user_id.unique().shape[0]
data_matrix = np.zeros((n_users, n_items))
train_data = turicreate.SFrame(ratings)

#Training the model
item_sim_model = turicreate.item_similarity_recommender.create(train_data, user_id='user_id', item_id='item_id', target='rating', similarity_type='cosine')

#Making recommendations
item_sim_recomm = item_sim_model.recommend(users=[1,2,3,4,5],k=5)
item_sim_recomm.print_rows(num_rows=25)


reader = Reader(rating_scale=(-1, 1))
data = Dataset.load_from_df(ratings[['user_id', 'item_id', 'rating']], reader)
trainset = data.build_full_trainset();
cross_validate(NormalPredictor(), data, cv=2)
algo = SVD()
cross_validate(algo, data, measures=['RMSE', 'MAE'], cv=5, verbose=True)
algo.fit(trainset)
testset = trainset.build_anti_testset()
predictions = algo.test(testset)
top_n = get_top_n(predictions, n=5)

# Print the recommended items for each user
for uid, user_ratings in top_n.items():
    print(uid, [iid for (iid, _) in user_ratings])



# for line in ratings.itertuples():
#     data_matrix[line[1]-1, line[2]-1] = line[3]
#
# user_similarity = pairwise_distances(data_matrix, metric='cosine')
# item_similarity = pairwise_distances(data_matrix.T, metric='cosine')
# user_prediction = predict(data_matrix, user_similarity, type='user')
# item_prediction = predict(data_matrix, item_similarity, type='item')
# print(user_prediction)
# print(item_prediction)


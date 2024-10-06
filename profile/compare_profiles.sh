# run this script from the root directory of the new branch
# (sh profile/compare_profiles.sh)
# it will print out the net time (overall time minus loading time) of the 
# new branch, the net time of main, and the ratio of: 
# net time of new branch divided by the net time of main.
cd profile
python -m card_profiler
RC1=$?
echo "New branch net runtime (multiplied by 1000 to become an integer): $RC1"
mv logs/benchmark_cards.prof logs/benchmark_cards_new_branch.prof
cd ..
git checkout main
cd profile
python -m card_profiler
RC2=$?
echo "Main branch net runtime (multiplied by 1000 to become an integer): $RC2"
echo "ratio of net times:  new_branch / main_branch is the following:"
echo "scale = 3; $RC1/$RC2" | bc
mv logs/benchmark_cards.prof logs/benchmark_cards_main.prof

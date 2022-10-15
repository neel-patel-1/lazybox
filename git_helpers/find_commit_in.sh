#!/bin/bash

pr_usage_exit()
{
	message=$1
	exit_code=$2

	if [ ! "$message" = "" ]
	then
		echo
		echo "$message"
		echo
	fi
	echo "Usage: $0 [OPTION]... <commit range>"
	echo
	echo "	Find a commit in <commit range> that has the author name and"
	echo "	subject of <commit>"
	echo
	echo "OPTION"
	echo "  --hash_only		Print hash only"
	echo "  --commit <hash>		Hash of the commit to find"
	echo "  --title <title>		Title of the commit to find"
	echo "  --author <author>	Author of the commit to find"
	exit $exit_code
}

hash_only="false"
while [ $# -ne 0 ]
do
	case $1 in
	"--hash_only")
		hash_only="true"
		shift 1
		continue
		;;
	"--commit")
		if [ $# -lt 2 ]
		then
			pr_usage_exit "--commit wrong" 1
		fi
		commit_to_find=$2
		shift 2
		continue
		;;
	"--title")
		if [ $# -lt 2 ]
		then
			pr_usage_exit "--title wrong" 1
		fi
		title_to_find=$2
		shift 2
		continue
		;;
	"--author")
		if [ $# -lt 2 ]
		then
			pr_usage_exit "<author> is not given" 1
		fi
		author=$2
		shift 2
		continue
		;;
	*)
		if [ $# -ne 1 ]
		then
			pr_usage_exit "should have <commit range>" 1
		fi
		break
		;;
	esac
done

if [ $# -ne 1 ]
then
	pr_usage_exit "should have <commit range>" 1
fi
commit_range=$1

if [ "$commit_to_find" = "" ] && [ "$title_to_find" = "" ]
then
	pr_usage_exit "--commit or --title should given" 1
fi

if [ "$title_to_find" = "" ]
then
	subject=$(git log -n 1 "$commit_to_find" --pretty=%s)
else
	subject="$title_to_find"
fi

if [ "$author" = "" ] && [ ! "$commit_to_find" = "" ]
then
	author=$(git log -n 1 "$commit_to_find" --pretty=%an)
fi

if [ "$author" = "" ]
then
	hash_subject=$(git log --oneline "$commit_range" | \
		awk '{print $(NF-1)}' | grep -i -m 1 "$subject")
else
	hash_subject=$(git log --author="$author" --oneline "$commit_range" | \
		awk '{print $(NF-1)}' | grep -i -m 1 "$subject")
fi

if [ "$hash_subject" = "" ]
then
	exit 1
fi

if [ "$hash_only" = "true" ]
then
	simple_hash=$(echo "$hash_subject" | awk '{print $1}')
	git log --pretty=%H -n 1 "$simple_hash"
	exit
fi

echo "$hash_subject"
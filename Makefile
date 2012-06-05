all:

	echo "note: if this fails at lines starting with \"&\" and \"@\" characters, update less to the latest version:"
	echo "      # npm install less"
	lessc lizard_blockbox/static/lizard_blockbox/lizard_blockbox.less lizard_blockbox/static/lizard_blockbox/lizard_blockbox.css
	coffee -c lizard_blockbox/static/lizard_blockbox/blockbox.coffee

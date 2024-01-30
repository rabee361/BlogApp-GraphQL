import graphene
from graphene_django import DjangoObjectType
from .models import *
from .filters import *
from graphene_django.filter import DjangoFilterConnectionField 
from graphql_jwt.decorators import login_required
from graphql_jwt.shortcuts import create_refresh_token, get_token
import graphql_jwt
from django.contrib.auth import get_user_model , authenticate
from graphene import relay




#---------------------------------- Model Types -------------------------------------- # 


class UserType(DjangoObjectType):
    class Meta:
        model = get_user_model()
        exclude = ['password']


class PostType(DjangoObjectType):
    class Meta:
        model = Post
        interfaces = (relay.Node,)
        filter_fields = {
            'content': ['startswith']
        }

class AuthorType(DjangoObjectType):
    class Meta:
        model = Author
        interfaces = (relay.Node,)
        filterset_class = AuthorFilter

    
class CommentType(DjangoObjectType):
    class Meta:
        model = Comment


class ReadingListType(DjangoObjectType):
    class Meta:
        model = ReadingList



###--------------------------------- Mutations --------------------------------###



#### Authentication & creating accounts ####

class LoginUser(graphene.Mutation):
    user = graphene.Field(UserType)
    token = graphene.String()
    refresh_token = graphene.String()

    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)

    def mutate(self,info,username,password):
        user = authenticate(username=username,password=password)
        if user is not None:
            token = get_token(user)
            refresh_token = create_refresh_token(user)
            return LoginUser(user=user,token=token,refresh_token=refresh_token)
        else:
            raise Exception('Invalid credentials')


class CreateUser(graphene.Mutation):
    user = graphene.Field(UserType)
    token = graphene.String()
    refresh_token = graphene.String()

    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        email = graphene.String(required=True)

    def mutate(self, info, username, password, email):
        user = get_user_model()(
            username=username,
            email=email,
        )
        user.set_password(password)
        user.save()
        token = get_token(user)
        refresh_token = create_refresh_token(user)
        return CreateUser(user=user, token=token, refresh_token=refresh_token)




class AddToReadingList(graphene.Mutation):
    reading_list = graphene.Field(ReadingListType)

    class Arguments:
        post_id = graphene.ID(required=True)

    def mutate(self,info,post_id):
        post = Post.objects.get(id=post_id)
        user = info.context.user
        reading_list = ReadingList.objects.get(user=user)
        reading_list.posts.add(post)
        return AddToReadingList(reading_list=reading_list)




######## Post Author ########

class CreateAuthor(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)

    author = graphene.Field(AuthorType)

    def mutate(self, info, name):
        author = Author.objects.create(name=name)
        author.save()
        return CreateAuthor(author=author)



class DeleteAuthor(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    message = graphene.String()

    def mutate(self,info,id):
        try:
            author = Author.objects.get(id=id)
            name = author.name
            author.delete()
            return DeleteAuthor(message=f"Author {name} deleted successfully")
        
        except Author.DoesNotExist:
            raise Exception("Author doesn't exist")



class UpdateAuthor(graphene.Mutation):
    author = graphene.Field(AuthorType)

    class Arguments:
        new_name = graphene.String(required=True)
        id = graphene.ID(required=True)

    def mutate(self,info,new_name,id):
        try:
            author = Author.objects.get(id=id)
            author.name = new_name
            author.save()
            return UpdateAuthor(author=author)
        
        except Author.DoesNotExist:
            raise Exception(f"Author with {id} doesn't exist")



class SubscribeToAuthor(graphene.Mutation):
    user = graphene.Field(UserType)
    subscribed_authors = graphene.List(AuthorType)

    class Arguments:
        author_id = graphene.ID(required=True)

    def mutate(self,info,author_id):
        user = info.context.user
        author = Author.objects.get(id=author_id)
        author.subscribers.add(user)
        subscribed_authors = user.author_set.all()
        return SubscribeToAuthor(user=user,subscribed_authors=subscribed_authors)



class UnSubscribe(graphene.Mutation):
    msg = graphene.String()

    class Arguments:
        author_id = graphene.ID(required=True)

    def mutate(root,info,author_id):
        user = info.context.user
        author = Author.objects.get(id=author_id)
        author.subscribers.remove(user)
        return UnSubscribe(msg=f"unsubscibed from the author {author.name}")
    

######## Posts ########
        
class CreatePost(graphene.Mutation):
    class Arguments:
        title = graphene.String()
        content = graphene.String()
        likes = graphene.Int()
        author_id = graphene.ID(required=True)

    post = graphene.Field(PostType)

    def mutate(self, info, title , content, likes,author_id):
        author = Author.objects.get(pk=author_id)
        post = Post.objects.create(title=title,content=content,author=author,likes=likes)
        post.save()
        return CreatePost(post=post)



class DeletePost(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    message = graphene.String()

    def mutate(self,info,id):
        try:
            post = Post.objects.get(id=id)
            post.delete()
            return DeletePost(message="Post deleted successfully")
        
        except Comment.DoesNotExist:
            raise Exception("Post doesn't exist")


######## Comments #########

class CreateComment(graphene.Mutation):
    class Arguments:
        author_id = graphene.ID(required=True)
        text = graphene.String()

    comment = graphene.Field(CommentType)

    def mutate(self,info,text,author_id):
        author = Author.objects.get(id=author_id)
        comment = Comment.objects.create(text=text,author=author)
        comment.save()
        return CreateComment(comment=comment)


class DeleteComment(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    message = graphene.String()

    def mutate(self,info,id):
        try:
            comment = Comment.objects.get(id=id)
            comment.delete()
            return DeleteComment(message="Comment deleted successfully")
        
        except Post.DoesNotExist:
            raise Exception("Comment doesn't exist")










class Mutation(graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    revoke_token = graphql_jwt.relay.Revoke.Field()
    create_user = CreateUser.Field()
    login_user = LoginUser.Field()
    subscribe_to_author = SubscribeToAuthor.Field()
    unsubscribe = UnSubscribe.Field()

    create_author = CreateAuthor.Field()
    update_author = UpdateAuthor.Field()
    delete_author = DeleteAuthor.Field()

    create_post = CreatePost.Field()
    delete_post = DeletePost.Field()
    
    create_comment = CreateComment.Field()
    delete_comment = DeleteComment.Field()

    add_to_reading_list = AddToReadingList.Field()





class Query(graphene.ObjectType):
    all_posts = DjangoFilterConnectionField(PostType)
    post = graphene.Field(PostType,id=graphene.Int())

    all_authors = graphene.List(AuthorType)
    author = graphene.Field(AuthorType,id=graphene.Int())

    all_comments = graphene.List(CommentType)
    comment = graphene.List(CommentType)

    all_my_reading_lists = graphene.List(ReadingListType)
    my_reading_list = graphene.Field(ReadingListType,list_id=graphene.ID(required=True))

    whoami = graphene.Field(UserType)
    users = graphene.List(UserType)


    @login_required
    def resolve_whoami(self, info):
        user = info.context.user
        return user


    @login_required
    def resolve_users(self, info):
        return get_user_model().objects.all()


    def resolve_all_authors(root, info):
        return Author.objects.all()


    def resolve_all_comments(root, info):
        return Comment.objects.all()


    def resolve_post(root, info, id):
        try:
            return Post.objects.get(pk=id)
        except Post.DoesNotExist:
            return None
        

    def resolve_all_my_reading_lists(root,info):
        user = info.context.user
        reading_lists = ReadingList.objects.filter(user=user)
        return reading_lists


    def resolve_my_reading_list(root,info,list_id):
        reading_list = ReadingList.objects.get(id=list_id)
        return reading_list



schema = graphene.Schema(query=Query, mutation=Mutation)

<template>
  <div class="container">
    <q-table :columns="columns" :rows="articles" flat bordered>
      <template v-slot:top>
        <div class="tableHeader">
          <h3>Articles list</h3>
          <div class="tableHeader_buttons">
            <q-btn @click="openNewPopup" label="Add article" color="primary" />
            <q-dialog v-model="addingNewArticle" persistent>
              <q-card>
                <q-card-section class="row items-center">
                  <div class="newArticle">
                    <div class="text-h5 text-center">Add new article</div>
                    <q-input
                      v-model="newArticle.title"
                      :rules="[(val) => !!val || 'Title is required']"
                      label="Title"
                      dense
                      outlined
                    />
                    <q-input
                      v-model="newArticle.content"
                      :rules="[(val) => !!val || 'Content is required']"
                      label="Content"
                      dense
                      outlined
                    />
                    <q-date
                      v-model="newArticle.releaseDate"
                      mask="MM/DD/YYYY"
                    />
                  </div>
                </q-card-section>
                <q-card-actions align="right">
                  <q-btn flat label="Cancel" color="primary" v-close-popup />
                  <q-btn
                    @click="addNew"
                    flat
                    label="Add"
                    color="primary"
                    :disabled="!newArticle.content || !newArticle.title"
                    v-close-popup
                  />
                </q-card-actions>
              </q-card>
            </q-dialog>
            <q-btn @click="fetchData" flat icon="refresh" color="primary" />
          </div>
        </div>
      </template>
      <template v-slot:body="props">
        <q-tr>
          <q-td key="articleId">
            {{ props.row.articleId }}
          </q-td>
          <q-td key="title">
            <q-input
              v-if="editedArticle && editedArticle?.articleId == props.row.articleId"
              v-model="editedArticle.title"
              :rules="[(val) => !!val || 'Title is required']"
              label="Title"
              outlined
              dense
            />
            <span v-else>
              {{ props.row.title }}
            </span>
          </q-td>
          <q-td key="content">
            <q-input
              v-if="editedArticle && editedArticle?.articleId == props.row.articleId"
              v-model="editedArticle.content"
              :rules="[(val) => !!val || 'Content is required']"
              label="Content"
              outlined
              dense
            />
            <span v-else>
              {{ props.row.content }}
            </span>
          </q-td>
          <q-td>
            <q-input
              v-if="editedArticle && editedArticle?.articleId == props.row.articleId"
              :model-value="editedArticle.releaseDate?.toLocaleDateString('en-us')"
              class="tableRow_dateInput"
              label="Release date"
              outlined
              dense
            >
              <template v-slot:append>
                <q-icon name="event" class="cursor-pointer">
                  <q-popup-proxy>
                    <q-date
                      :model-value="editedArticle.releaseDate?.toLocaleDateString('en-us')"
                      @update:model-value="setDate"
                      mask="MM/DD/YYYY"
                    >
                      <div class="row items-center justify-end">
                        <q-btn
                          v-close-popup
                          label="Close"
                          color="primary"
                          flat
                        />
                      </div>
                    </q-date>
                  </q-popup-proxy>
                </q-icon>
              </template>
            </q-input>
            <span v-else>
              {{ props.row.releaseDate?.toLocaleDateString('en-us') }}
            </span>
          </q-td>
          <q-td class="tableRow_edit">
            <div v-if="isEdited(props.row)">
              <q-btn @click="cancel()" flat icon="cancel" color="grey" />
              <q-btn @click="applyChanges" flat icon="check" color="positive" />
            </div>
            <div v-else>
              <q-btn
                @click="editRow(props.row)"
                flat
                icon="edit"
                color="grey"
              />
              <q-btn
                @click="deleteArt(props.row)"
                flat
                icon="delete"
                color="negative"
              />
            </div>
          </q-td>
        </q-tr>
      </template>
      <template v-slot:no-data>
        <div
          class="full-width row flex-center q-gutter-sm"
          style="margin: 20px"
        >
          <div class="text-h4">No data available</div>
        </div>
      </template>
    </q-table>
  </div>
  <q-dialog v-model="updatedAlert" position="top">
    <q-card>
      <q-card-section>
        <div class="text-h6">{{ actionSuccess ? 'Success' : 'Error' }}</div>
      </q-card-section>
      <q-card-section v-if="!actionSuccess" class="q-pt-none">
        {{ actionError }}
      </q-card-section>
      <q-card-actions align="right">
        <q-btn flat label="OK" color="primary" @click="closeAlert" />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import {
  addNewArticle,
  deleteArticle,
  getArticles,
  updateArticle,
} from 'src/api/articles';
import type { Article } from 'src/model/Article';
import type { Ref } from 'vue';
import { onMounted, ref } from 'vue';

const columns = [
  {
    name: 'id',
    required: true,
    label: 'Id',
    field: 'articleId',
    sortable: true,
    align: 'left',
  },
  {
    name: 'title',
    required: true,
    label: 'Title',
    field: 'title',
    sortable: true,
    align: 'left',
  },
  {
    name: 'content',
    required: true,
    label: 'Content',
    field: 'content',
    sortable: true,
    align: 'left',
  },
  {
    name: 'releaseDate',
    required: false,
    label: 'Release date',
    field: 'releaseDate',
    sortable: true,
    align: 'left',
  },
  {
    name: 'edit',
    field: 'edit',
    sortable: false,
    align: 'right',
  },
];

const articles: Ref<Article[]> = ref([]);
const editedArticle: Ref<Article | null> = ref(null);
const updatedAlert: Ref<boolean> = ref(false);
const actionSuccess: Ref<boolean> = ref(false);
const actionError: Ref<string> = ref('');
const addingNewArticle: Ref<boolean> = ref(false);
const newArticle: Ref<Article> = ref({} as Article);

const fetchData = async () => {
  try {
    const response = await getArticles();
    articles.value = response;
  } catch (err) {
    console.log(err);
  }
};

const isEdited = (article: Article) => {
  return editedArticle.value && editedArticle.value?.articleId === article.articleId;
};

const editRow = (article: Article) => {
  editedArticle.value = Object.assign({}, article);
};

const setDate = (dateString: string) => {
  if (editedArticle?.value) {
    editedArticle.value.releaseDate = new Date(dateString);
  }
};

const deleteArt = (article: Article) => {
  deleteArticle(article)
    .then(() => {
      actionSuccess.value = true;
      const index = articles.value.findIndex(
        (val) => val.articleId === article.articleId
      );
      if (index !== -1) {
        articles.value.splice(index, 1);
      }
    })
    .catch((e) => {
      actionError.value = e;
    })
    .finally(() => {
      updatedAlert.value = true;
    });
};

const cancel = () => {
  editedArticle.value = null;
};

const applyChanges = async () => {
  if (!editedArticle.value) return;

  updateArticle(editedArticle.value)
    .then(() => {
      actionSuccess.value = true;
      const index = articles.value.findIndex(
        (article) => article.articleId === editedArticle.value?.articleId
      );
      if (index !== -1) {
        articles.value[index].content = editedArticle.value.content;
        articles.value[index].title = editedArticle.value.title;
        articles.value[index].releaseDate = editedArticle.value.releaseDate;
      }
    })
    .catch((error) => {
      actionError.value = error;
    })
    .finally(() => {
      editedArticle.value = null;
      updatedAlert.value = true;
    });
};

const openNewPopup = () => {
  newArticle.value = {} as Article;
  addingNewArticle.value = true;
};

const addNew = () => {
  const article = newArticle.value as Article;
  if (article.releaseDate) {
    article.releaseDate = new Date(article.releaseDate);
  }

  addNewArticle(article)
    .then(() => {
      actionSuccess.value = true;
      fetchData();
    })
    .catch((e) => {
      actionError.value = e;
    })
    .finally(() => {
      updatedAlert.value = true;
    });
};

const closeAlert = () => {
  updatedAlert.value = false;
  actionError.value = '';
  actionSuccess.value = false;
};

onMounted(() => {
  fetchData();
});

</script>

<style>
.container {
  margin: 20px;
}
.tableHeader {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.tableHeader_buttons button {
  margin: 10px;
}
.q-table__top,
.q-table__bottom,
thead {
  background-color: aliceblue;
}
.tableRow_edit {
  width: 100px;
}
.q-field {
  margin-top: 10px;
}
.tableRow_dateInput {
  margin-bottom: 20px;
}
.newArticle {
  padding: 10px;
}
</style>

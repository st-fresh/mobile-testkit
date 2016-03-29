package com.couchbase.com.mobiletestkitapp;

import android.os.Bundle;
import android.provider.ContactsContract;
import android.support.design.widget.FloatingActionButton;
import android.support.design.widget.Snackbar;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.Toolbar;
import android.view.View;
import android.view.Menu;
import android.view.MenuItem;

import android.util.Log;

import com.couchbase.lite.Attachment;
import com.couchbase.lite.CouchbaseLiteException;
import com.couchbase.lite.Database;
import com.couchbase.lite.Document;
import com.couchbase.lite.Manager;
import com.couchbase.lite.SavedRevision;
import com.couchbase.lite.UnsavedRevision;
import com.couchbase.lite.android.AndroidContext;

import java.io.BufferedReader;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.util.HashMap;
import java.util.Map;

public class MainActivity extends AppCompatActivity {

    public static final String DB_NAME = "testkit";
    public static final String TAG = "testkit";

    private Database database;
    private Manager manager;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
//        Toolbar toolbar = (Toolbar) findViewById(R.id.toolbar);
//        setSupportActionBar(toolbar);
//
//        FloatingActionButton fab = (FloatingActionButton) findViewById(R.id.fab);
//        fab.setOnClickListener(new View.OnClickListener() {
//            @Override
//            public void onClick(View view) {
//                Snackbar.make(view, "Replace with your own action", Snackbar.LENGTH_LONG)
//                        .setAction("Action", null).show();
//            }
//        });

        helloCBL();
    }

    private void helloCBL() {

        try {
            setManagerInstance();
            setDatabaseInstance();
        } catch (Exception e) {
            Log.e(TAG, "Error getting database", e);
            return;
        }

        // Create document
        String documentId = createDocument();
        Document retrievedDocument = getDatabaseInstance().getDocument(documentId);
        Log.d(TAG, "retrievedDocument=" + String.valueOf(retrievedDocument.getProperties()));

        // Update doc
        updateDocument(documentId);
        retrievedDocument = getDatabaseInstance().getDocument(documentId);
        Log.d(TAG, "retrievedDocument=" + String.valueOf(retrievedDocument.getProperties()));

        // Add attachment
        addAttachment(documentId);

        // Get attachment
        retrievedDocument = getDatabaseInstance().getDocument(documentId);
        SavedRevision saved = retrievedDocument.getCurrentRevision();
        Attachment attachment = saved.getAttachment("binaryData");

        InputStream content;
        try {
            content = attachment.getContent();
        } catch (CouchbaseLiteException e) {
            Log.e(TAG, "Failed to get attachment content", e);
            return;
        }
        BufferedReader reader = new BufferedReader(new InputStreamReader(content));
        StringBuffer values = new StringBuffer();

        int i = 0;
        while(i++ < 4) {
            try {
                values.append(reader.read() + " ");
            } catch (IOException e) {
                Log.e(TAG, "Error reading stream", e);
            }
        }

        Log.v("LaurentActivity", "The docID: " + documentId + ", attachment contents was: " + values.toString());

        // delete the document
        try {
            retrievedDocument.delete();
            Log.d (TAG, "Deleted document, deletion status = " + retrievedDocument.isDeleted());
        } catch (CouchbaseLiteException e) {
            Log.e (TAG, "Cannot delete document", e);
        }

    }

    private String createDocument() {
        Document document = getDatabaseInstance().createDocument();
        String documentId = document.getId();
        Map<String, Object> map = new HashMap<String, Object>();
        map.put("name", "Big Party");
        map.put("location", "My House");
        try {
            document.putProperties(map);
        } catch (CouchbaseLiteException e) {
            Log.e(TAG, "Error putting doc", e);
        }
        return documentId;
    }

    private void updateDocument(String documentId) {
        Document document = getDatabaseInstance().getDocument(documentId);
        try {
            Map<String, Object> updatedProperties = new HashMap<String, Object>();
            updatedProperties.putAll(document.getProperties());
            updatedProperties.put("description", "Everyone is invited!");
            updatedProperties.put("address", "123 My Street");
            document.putProperties(updatedProperties);
        } catch (CouchbaseLiteException e) {
            Log.e(TAG, "Error updating", e);
        }
    }

    private void addAttachment(String documentId) {
        Document document = getDatabaseInstance().getDocument(documentId);
        try {
            ByteArrayInputStream inputStream = new ByteArrayInputStream(new byte[] { 0, 0, 0, 0 });
            UnsavedRevision revision = document.getCurrentRevision().createRevision();
            revision.setAttachment("binaryData", "application/octet-stream", inputStream);
            revision.save();
        } catch (CouchbaseLiteException e) {
            Log.e(TAG, "Error saving attachment", e);
        }
    }

    private void setManagerInstance() throws IOException {
        if (this.manager == null) {
            this.manager = new Manager(new AndroidContext(this), Manager.DEFAULT_OPTIONS);
        }
    }

    private void setDatabaseInstance() throws CouchbaseLiteException {
        if (this.database == null) {
            this.database = this.manager.getDatabase(DB_NAME);
        }
    }

    public Database getDatabaseInstance() {
        return this.database;
    }

//    @Override
//    public boolean onCreateOptionsMenu(Menu menu) {
//        // Inflate the menu; this adds items to the action bar if it is present.
//        getMenuInflater().inflate(R.menu.menu_main, menu);
//        return true;
//    }
//
//    @Override
//    public boolean onOptionsItemSelected(MenuItem item) {
//        // Handle action bar item clicks here. The action bar will
//        // automatically handle clicks on the Home/Up button, so long
//        // as you specify a parent activity in AndroidManifest.xml.
//        int id = item.getItemId();
//
//        //noinspection SimplifiableIfStatement
//        if (id == R.id.action_settings) {
//            return true;
//        }
//
//        return super.onOptionsItemSelected(item);
//    }
}
